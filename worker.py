"""
WARP Loop - Temporal Worker
============================
Run this to start processing WARP workflows.

    python worker.py

Requires a running Temporal server (e.g., `temporal server start-dev`).
"""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from workflow import WarpWorkflow
from activities import (
    route_action,
    search_passages,
    create_outline,
    write_section,
    extend_outline,
    format_report,
)

TASK_QUEUE = "warp-queue"


async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[WarpWorkflow],
        activities=[
            route_action,
            search_passages,
            create_outline,
            write_section,
            extend_outline,
            format_report,
        ],
    )

    print(f"WARP worker listening on queue: {TASK_QUEUE}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
