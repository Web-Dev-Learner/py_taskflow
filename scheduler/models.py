from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from .services.db import Base


# ======================================
# 🧾 Task Table — for scheduling & retries
# ======================================
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    command = Column(String, nullable=False)

    # ✅ timezone-aware scheduling timestamp
    scheduled_at = Column(DateTime(timezone=True), nullable=False)

    status = Column(String, default="scheduled")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # ✅ lifecycle tracking
    picked_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))

    # ✅ retry tracking
    retry_at = Column(DateTime(timezone=True))
    retry_count = Column(Integer, default=0)


# ======================================
# 💓 Worker Table — for heartbeat tracking
# ======================================
class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)
    hostname = Column(String, unique=True)
    last_heartbeat = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="alive")
