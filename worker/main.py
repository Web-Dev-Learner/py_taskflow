import asyncio
import grpc
import subprocess
import sys
import os
import socket
from datetime import datetime, timezone
from dotenv import load_dotenv
import uuid

from proto import task_pb2, task_pb2_grpc

# import task_pb2, task_pb2_grpc

# Load environment variables from .env
load_dotenv()


# Allow relative imports
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.logger import setup_logger
from scheduler.services.db import AsyncSessionLocal
from scheduler.models import Task

logger = setup_logger("Worker")

# Limit concurrent tasks (optional tuning)
SEM = asyncio.Semaphore(3)

# Coordinator heartbeat port
# COORDINATOR_GRPC_PORT = 50052

COORDINATOR_GRPC_PORT = int(os.getenv("COORDINATOR_GRPC_PORT", "50052"))



# ==============================
# 🧠 gRPC Task Execution Service
# ==============================
class WorkerService(task_pb2_grpc.WorkerServiceServicer):
    async def ExecuteTask(self, request, context):
        """Handles incoming task execution requests."""
        async with SEM:
            task_id = request.id
            command = request.command
            logger.info(f"🧾 Received task {task_id}: {command}")

            async with AsyncSessionLocal() as session:
                task = await session.get(Task, task_id)
                if task:
                    task.started_at = datetime.now(timezone.utc)
                    await session.commit()

            try:
                # Run the command asynchronously
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    logger.info(f"✅ Task {task_id} completed successfully.")
                    status = "done"
                    message = stdout.decode().strip() or "Executed successfully"
                    completed_at = datetime.now(timezone.utc)
                else:
                    logger.error(f"❌ Task {task_id} failed: {stderr.decode().strip()}")
                    status = "failed"
                    message = stderr.decode().strip()
                    completed_at = datetime.now(timezone.utc)

                # Update DB lifecycle timestamps
                async with AsyncSessionLocal() as session:
                    task = await session.get(Task, task_id)
                    if task:
                        task.status = status
                        if status == "done":
                            task.completed_at = completed_at
                        else:
                            task.failed_at = completed_at
                        await session.commit()

                return task_pb2.TaskResponse(id=task_id, status=status, message=message)

            except Exception as e:
                logger.error(f"🔥 Exception while executing task {task_id}: {e}")
                async with AsyncSessionLocal() as session:
                    task = await session.get(Task, task_id)
                    if task:
                        task.status = "failed"
                        task.failed_at = datetime.now(timezone.utc)
                        await session.commit()
                return task_pb2.TaskResponse(
                    id=task_id, status="failed", message=str(e)
                )


# ==============================
# 💓 Worker Heartbeat Sender (with .env support)
# ==============================
async def send_heartbeat():
    """Periodically send heartbeat pings to Coordinator."""
    # Read settings from .env (with defaults)
    base_name = os.getenv("WORKER_NAME", "Default-Worker")
    instance_id = str(uuid.uuid4())[:6]  # short unique suffix
    hostname = f"{base_name}-{instance_id}"

    # coordinator_host = os.getenv("COORDINATOR_HOST", "coordinator")
    # coordinator_port = os.getenv("COORDINATOR_HEARTBEAT_PORT", "50052")

    coordinator_host = os.getenv("COORDINATOR_HOST")
    coordinator_port = os.getenv("COORDINATOR_HEARTBEAT_PORT")


    interval = int(os.getenv("WORKER_HEARTBEAT_INTERVAL", 10))

    while True:
        try:
            async with grpc.aio.insecure_channel(f"{coordinator_host}:{coordinator_port}") as channel:
                stub = task_pb2_grpc.WorkerServiceStub(channel)
                req = task_pb2.HeartbeatRequest(hostname=hostname)
                await stub.Heartbeat(req)
                logger.info(f"💓 Sent heartbeat from {hostname}")
        except Exception as e:
            logger.warning(f"⚠️ Heartbeat failed: {e}")
        await asyncio.sleep(interval)



# ==============================
# 🚀 Start Worker Services
# ==============================
async def serve():
    """Start Worker gRPC server for task execution."""
    server = grpc.aio.server()
    task_pb2_grpc.add_WorkerServiceServicer_to_server(WorkerService(), server)


    worker_port = int(os.getenv("WORKER_GRPC_PORT", "50051"))
    server.add_insecure_port(f"[::]:{worker_port}")

    await server.start()
    logger.info(f"⚙️ Worker service running on port {worker_port}...")
    await server.wait_for_termination()

# ✅ Proper async entrypoint (fix for asyncio.gather issue)
async def main():
    await asyncio.gather(serve(), send_heartbeat())


if __name__ == "__main__":
    asyncio.run(main())
