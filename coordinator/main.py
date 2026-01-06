import asyncio
import grpc
from datetime import datetime, timezone, timedelta
from sqlalchemy.future import select

# from scheduler.services.db import AsyncSessionLocal

from scheduler.services.db import AsyncSessionLocal

from scheduler.models import Task, Worker

# import task_pb2, task_pb2_grpc
from proto import task_pb2, task_pb2_grpc

import sys, os

# Fix import path for CLI runs
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# from utils.logger import setup_logger
from utils.logger import setup_logger

logger = setup_logger("Coordinator")

CHECK_INTERVAL = 5          # seconds between polling cycles
MAX_RETRIES = 3             # maximum retry attempts per task
RETRY_DELAY = 60            # seconds before retry
RETRY_BACKOFF = True        # exponential backoff toggle
HEARTBEAT_TIMEOUT = 30      # seconds after which worker marked as "dead"


# ===============================
#  Task Dispatch Logic
# ===============================
async def dispatch_task(task):
    """Send the task to a Worker via gRPC with transient retry."""
    retries = 0
    while retries < 2:  # internal retries for network issues
        try:
            worker_host = os.getenv("WORKER_HOST", "localhost")
            worker_port = os.getenv("WORKER_GRPC_PORT", "50051")

            async with grpc.aio.insecure_channel(f"{worker_host}:{worker_port}") as channel:

                stub = task_pb2_grpc.WorkerServiceStub(channel)
                req = task_pb2.TaskRequest(id=task.id, command=task.command)
                resp = await stub.ExecuteTask(req)
                logger.info(f"✅ Task {task.id}: {resp.status} - {resp.message}")
                return True
        except Exception as e:
            retries += 1
            logger.warning(f"⚠️ gRPC dispatch attempt {retries}/2 failed for Task {task.id}: {e}")
            await asyncio.sleep(2)
    return False


# ===============================
#  Main Polling Loop
# ===============================
async def poll_and_dispatch():
    """Continuously poll DB for due or retryable tasks and dispatch them."""
    logger.info("🔄 Coordinator polling loop started.")

    while True:
        async with AsyncSessionLocal() as session:
            now = datetime.now(timezone.utc)
            result = await session.execute(
                select(Task).where(
                    ((Task.scheduled_at <= now) | (Task.retry_at <= now)),
                    Task.status.in_(["scheduled", "retrying"])
                )
            )
            tasks = result.scalars().all()

            if tasks:
                logger.info(f"📦 Found {len(tasks)} task(s) ready to dispatch.")
            else:
                logger.debug("No due tasks this cycle.")

            for task in tasks:
                task.status = "running"
                task.picked_at = datetime.now(timezone.utc)
                await session.commit()

                logger.info(f"🚀 Dispatching Task {task.id}: {task.command}")
                success = await dispatch_task(task)

                if not success:
                    task.retry_count += 1
                    if task.retry_count < MAX_RETRIES:
                        delay = RETRY_DELAY * (2 ** (task.retry_count - 1)) if RETRY_BACKOFF else RETRY_DELAY
                        task.retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
                        task.status = "retrying"
                        logger.warning(f"⏱️ Task {task.id} will retry in {delay}s (count={task.retry_count}).")
                    else:
                        task.status = "failed"
                        task.failed_at = datetime.now(timezone.utc)
                        logger.error(f"❌ Task {task.id} reached max retries ({MAX_RETRIES}).")
                    await session.commit()

        await asyncio.sleep(CHECK_INTERVAL)


# ===============================
#  Heartbeat Reception Service
# ===============================
class HeartbeatService(task_pb2_grpc.WorkerServiceServicer):
    async def Heartbeat(self, request, context):
        """Handle incoming worker heartbeat."""
        hostname = request.hostname
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Worker).where(Worker.hostname == hostname))
            worker = result.scalars().first()
            if worker:
                worker.last_heartbeat = datetime.now(timezone.utc)
                worker.status = "alive"
            else:
                worker = Worker(
                    hostname=hostname,
                    status="alive",
                    last_heartbeat=datetime.now(timezone.utc)
                )
                session.add(worker)
            await session.commit()
        logger.info(f"💚 Heartbeat received from {hostname}")
        return task_pb2.HeartbeatResponse(status="ack", message="Heartbeat updated")


# ===============================
#  Dead Worker Cleanup
# ===============================
async def check_dead_workers():
    """Periodically scan for dead workers (no heartbeat for 30s)."""
    while True:
        async with AsyncSessionLocal() as session:
            threshold = datetime.now(timezone.utc) - timedelta(seconds=HEARTBEAT_TIMEOUT)
            result = await session.execute(select(Worker).where(Worker.last_heartbeat < threshold))
            dead_workers = result.scalars().all()

            for w in dead_workers:
                if w.status != "dead":
                    w.status = "dead"
                    logger.warning(f"💀 Worker {w.hostname} marked as dead.")
            await session.commit()

        await asyncio.sleep(HEARTBEAT_TIMEOUT)


# ===============================
#  Coordinator Entry Point
# ===============================
async def serve_heartbeat():
    """Start gRPC server to receive heartbeats."""
    server = grpc.aio.server()
    task_pb2_grpc.add_WorkerServiceServicer_to_server(HeartbeatService(), server)

    heartbeat_port = int(os.getenv("COORDINATOR_HEARTBEAT_PORT", "50052"))
    server.add_insecure_port(f"[::]:{heartbeat_port}")

    await server.start()
    logger.info(f"💓 Heartbeat listener running on port {heartbeat_port}...")
    await server.wait_for_termination()


async def main():
    """Run all coordinator services concurrently."""
    await asyncio.gather(
        poll_and_dispatch(),
        check_dead_workers(),
        serve_heartbeat()
    )


if __name__ == "__main__":
    logger.info("⚙️ Coordinator service started.")
    asyncio.run(main())
