# ======================================================
#  File: scheduler/api/routes.py
# ======================================================

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
import asyncio
import json

from ..services.db import get_db, AsyncSessionLocal
from ..models import Task, Worker
from .schemas import TaskCreate, TaskRead
from scheduler.core.limiter import limiter

router = APIRouter()

# ======================================================
#  Task Scheduling + Status Endpoints
# ======================================================

@router.post("/schedule", response_model=TaskRead)
@limiter.limit("5/minute")
async def schedule_task(
    request: Request,
    task: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
# async def schedule_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Schedule a new task and store in DB."""
    scheduled_at = task.scheduled_at
    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
    else:
        scheduled_at = scheduled_at.astimezone(timezone.utc)

    new_task = Task(command=task.command, scheduled_at=scheduled_at)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


@router.get("/status", response_model=TaskRead)
async def get_task_status(task_id: int, db: AsyncSession = Depends(get_db)):
    """Get the current status of a scheduled task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ======================================================
# NEW: Recent Tasks Endpoint for Dashboard Table
# ======================================================

@router.get("/tasks")
@limiter.limit("20/minute")
async def list_recent_tasks(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
# async def list_recent_tasks(db: AsyncSession = Depends(get_db)):


    """
    Return a list of recent tasks (latest 20) for dashboard display.
    Used by React's TaskTable.jsx.
    """
    result = await db.execute(select(Task).order_by(Task.created_at.desc()).limit(20))
    tasks = result.scalars().all()

    data = []
    for t in tasks:
        data.append({
            "id": t.id,
            "command": t.command,
            "status": t.status,
            "scheduled_at": t.scheduled_at.isoformat() if t.scheduled_at else None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "started_at": t.started_at.isoformat() if t.started_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "failed_at": t.failed_at.isoformat() if t.failed_at else None,
        })

    return JSONResponse(data)


# ======================================================
#  Worker Monitoring (for Dashboard)
# ======================================================

@router.get("/workers")
@limiter.limit("30/minute")
async def list_workers(
    request: Request,
    db: AsyncSession = Depends(get_db)
):

# async def list_workers(db: AsyncSession = Depends(get_db)):
    """List all workers with their status (alive/dead)."""
    result = await db.execute(select(Worker))
    workers = result.scalars().all()

    out = [
        {
            "id": w.id,
            "hostname": w.hostname,
            "status": w.status,
            "last_heartbeat": w.last_heartbeat.isoformat() if w.last_heartbeat else None,
        }
        for w in workers
    ]
    return JSONResponse(out)


# ======================================================
#  Metrics (JSON + Prometheus)
# ======================================================

@router.get("/metrics")
async def metrics_json(db: AsyncSession = Depends(get_db)):
    """Return system metrics as JSON for dashboard."""
    result = await db.execute(select(Task))
    tasks = result.scalars().all()

    total = len(tasks)
    by_status = {}
    running = 0
    failed = 0
    done = 0
    exec_times = []

    for t in tasks:
        s = t.status or "unknown"
        by_status[s] = by_status.get(s, 0) + 1
        if s == "running":
            running += 1
        elif s == "failed":
            failed += 1
        elif s == "done":
            done += 1

        if t.started_at and t.completed_at:
            exec_times.append((t.completed_at - t.started_at).total_seconds())

    avg_exec = sum(exec_times) / len(exec_times) if exec_times else 0.0

    payload = {
        "total_tasks": total,
        "tasks_by_status": by_status,
        "tasks_running": running,
        "tasks_failed": failed,
        "tasks_done": done,
        "avg_execution_seconds": avg_exec,
    }

    return JSONResponse(payload)


@router.get("/prometheus-metrics")
async def metrics_prometheus(db: AsyncSession = Depends(get_db)):
    """Expose Prometheus-compatible metrics (optional)."""
    result = await db.execute(select(Task))
    tasks = result.scalars().all()

    total = len(tasks)
    running = sum(1 for t in tasks if t.status == "running")
    failed = sum(1 for t in tasks if t.status == "failed")
    done = sum(1 for t in tasks if t.status == "done")

    gauge_total = Gauge("pytaskflow_total_tasks", "Total number of tasks")
    gauge_running = Gauge("pytaskflow_tasks_running", "Currently running tasks")
    gauge_failed = Gauge("pytaskflow_tasks_failed", "Failed tasks")
    gauge_done = Gauge("pytaskflow_tasks_done", "Completed tasks")

    gauge_total.set(total)
    gauge_running.set(running)
    gauge_failed.set(failed)
    gauge_done.set(done)

    output = generate_latest()
    return Response(content=output, media_type=CONTENT_TYPE_LATEST)


# ======================================================
#  SSE — Server-Sent Events for Real-Time Updates
# ======================================================

async def _worker_event_generator(poll_interval: float = 2.0):
    """Yields worker updates periodically for SSE."""
    last_snapshot = None

    while True:
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(select(Worker))
                workers = result.scalars().all()
            except Exception:
                yield "event: error\ndata: {}\n\n".format(json.dumps({"msg": "db error"}))
                await asyncio.sleep(poll_interval)
                continue

        snapshot = [
            {"id": w.id, "hostname": w.hostname, "status": w.status,
             "last_heartbeat": w.last_heartbeat.isoformat() if w.last_heartbeat else None}
            for w in sorted(workers, key=lambda x: x.id)
        ]

        if snapshot != last_snapshot:
            data = json.dumps({
                "workers": snapshot,
                "ts": datetime.now(timezone.utc).isoformat()
            })
            yield f"event: workers\ndata: {data}\n\n"
            last_snapshot = snapshot

        await asyncio.sleep(poll_interval)


@router.get("/events")
async def stream_worker_events(request: Request):
    """
    SSE endpoint that streams worker updates.
    React frontend connects to this for live updates.
    """
    generator = _worker_event_generator()
    return StreamingResponse(generator, media_type="text/event-stream")
