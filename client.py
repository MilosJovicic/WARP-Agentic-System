"""
WARP Loop - Client
===================
Trigger a WARP report generation workflow.

    python client.py "How do graph databases improve manufacturing supply chains?"
"""

import asyncio
import json
import sys

from temporalio.client import Client

from workflow import WarpWorkflow
from models import WarpState

TASK_QUEUE = "warp-queue"


async def run_warp(query: str, max_iterations: int = 10) -> str:
    client = await Client.connect("localhost:7233")

    # Build initial state
    initial_state = WarpState(
        query=query,
        max_iterations=max_iterations,
    )

    # Execute workflow
    result_json = await client.execute_workflow(
        WarpWorkflow.run,
        initial_state.model_dump_json(),
        id=f"warp-{hash(query) % 10000:04d}",
        task_queue=TASK_QUEUE,
    )

    # Parse and display result
    final_state = WarpState.model_validate_json(result_json)

    print("\n" + "=" * 60)
    print("WARP REPORT COMPLETE")
    print("=" * 60)
    print(f"Query: {final_state.query}")
    print(f"Iterations: {final_state.iteration}")
    print(f"Action history: {' → '.join(final_state.action_history)}")
    print(f"Passages retrieved: {len(final_state.passages)}")
    print(f"Sections drafted: {len(final_state.drafted_sections)}")
    print("=" * 60)
    print()

    if final_state.final_report:
        print(final_state.final_report)
    else:
        print("WARNING: No final report generated")

    return result_json


def main():
    query = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "How do graph databases improve manufacturing supply chains?"
    )
    asyncio.run(run_warp(query))


if __name__ == "__main__":
    main()
