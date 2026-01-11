# PyTaskFlow – Distributed Task Scheduler

PyTaskFlow is a distributed task scheduling and execution system built using Python , FastAPI, gRPC, PostgreSQL, React, and Docker.  
It enables reliable scheduling, asynchronous execution, automatic retries, worker health monitoring, and real-time observability.  
The system  uses gRPC for internal coordination, and is deployed using Docker in a production-style cloud setup.

---

 **Demo Video:**  [Click here to watch the demo](https://drive.google.com/file/d/1u_xSB583wZX62AgEJFIhcYrvgo8Fs2X7/view?usp=sharing)

---
## Key Features

<ul>
  <li>Distributed task scheduling and execution</li>
  <li>Time-based (future) task scheduling</li>
  <li>Asynchronous task execution</li>
  <li>Full task lifecycle tracking</li>
  <li>Automatic retries with exponential backoff</li>
  <li>Worker heartbeat and liveness detection</li>
  <li>Real-time monitoring dashboard</li>
  <li>Structured, color-coded logging</li>
  <li>Fully Dockerized microservices</li>
  <li>Cloud-deployable on AWS</li>
</ul>

---

## Problem Statement

In real-world systems, background jobs must be:

<ul>
  <li>Scheduled reliably</li>
  <li>Executed asynchronously</li>
  <li>Retried on failure</li>
  <li>Recoverable after restarts</li>
  <li>Scalable across multiple workers</li>
  <li>Observable in real time</li>
</ul>

PyTaskFlow addresses these challenges by separating responsibilities into well-defined services that communicate using REST and gRPC, while persisting system state in a durable PostgreSQL database.

---

## System Architecture

<pre>
User
 ↓
React Dashboard
 ↓ (REST / SSE)
Scheduler (FastAPI)
 ↓ (Durable State)
PostgreSQL
 ↓ (Periodic Querying)
Coordinator
 ↓ (gRPC)
Worker(s)
 ↑ (Heartbeat)
Coordinator
</pre>

---

## Architectural Principles

<ul>
  <li>Separation of concerns</li>
  <li>Microservice-style architecture</li>
  <li>Control plane vs execution plane separation</li>
  <li>Async and non-blocking I/O</li>
  <li>Fault isolation and observability</li>
</ul>

---

## Technology Stack

### Backend
<ul>
  <li>Python 3.12</li>
  <li>FastAPI (REST API)</li>
  <li>SQLAlchemy (Async ORM)</li>
  <li>PostgreSQL</li>
  <li>gRPC with Protocol Buffers</li>
  <li>asyncio</li>
</ul>

### Frontend
<ul>
  <li>React </li>
  <li>Vite</li>
  <li>Tailwind CSS</li>
  <li>Server-Sent Events (SSE)</li>
</ul>

### DevOps / Infrastructure
<ul>
  <li>Docker</li>
  <li>Docker Compose</li>
  <li>Nginx </li>
  <li>AWS EC2 </li>
  <li>Let’s Encrypt SSL (Certbot)</li>
  <li>DuckDNS</li>
</ul>

### Observability
<ul>
  <li>structlog</li>
  <li>colorlog</li>
  <li>Health check endpoints</li>
  <li>Metrics endpoints (JSON and Prometheus-style)</li>
</ul>

---

## Core Services

### Scheduler (FastAPI – REST API)
<ul>
  <li>Accepts task submissions</li>
  <li>Validates input using Pydantic</li>
  <li>Persists tasks in PostgreSQL</li>
  <li>Exposes REST APIs for dashboard consumption</li>
  <li>Provides health and metrics endpoints</li>
  <li>Streams real-time updates via SSE</li>
</ul>

### Coordinator (gRPC – Control Plane)
<ul>
  <li>Periodically queries the database for due tasks</li>
  <li>Dispatches tasks to workers via gRPC</li>
  <li>Tracks worker heartbeats</li>
  <li>Detects dead workers</li>
  <li>Handles retries with exponential backoff</li>
</ul>

### Worker (gRPC – Execution Plane)
<ul>
  <li>Executes task commands asynchronously</li>
  <li>Limits concurrency using semaphores</li>
  <li>Reports execution results</li>
  <li>Sends periodic heartbeats</li>
</ul>

### React Dashboard
<ul>
  <li>Schedule new tasks</li>
  <li>View task history</li>
  <li>Monitor worker health</li>
  <li>Observe live system metrics</li>
</ul>

---

## Database Design

### Task Table
<ul>
  <li>Full task lifecycle tracking</li>
  <li>created → scheduled → picked → running → completed / failed</li>
  <li>Execution timestamps</li>
  <li>Retry count and retry scheduling</li>
</ul>

### Worker Table
<ul>
  <li>Worker identity</li>
  <li>Last heartbeat timestamp</li>
  <li>Alive / dead status</li>
</ul>

---

## gRPC and Protocol Buffers

<ul>
  <li>Internal service communication via gRPC</li>
  <li>Strongly-typed contracts using Protocol Buffers</li>
  <li>Single source of truth: <code>task.proto</code></li>
</ul>

---

## Observability and Monitoring

<ul>
  <li>Structured, service-specific logging</li>
  <li>Color-coded log levels</li>
  <li>Health check endpoints</li>
  <li>Metrics APIs</li>
  <li>Real-time worker monitoring via SSE</li>
</ul>

---

## AWS Deployment (Docker-based)

<ul>
  <li>AWS EC2 </li>
  <li>Dockerized services:
    <ul>
      <li>Scheduler</li>
      <li>Coordinator</li>
      <li>Worker(s)</li>
      <li>PostgreSQL</li>
    </ul>
  </li>
  <li>Docker Compose for orchestration</li>
  <li>Nginx as reverse proxy and HTTPS termination</li>
</ul>

---




