# WARP Loop — Temporal + PydanticAI Implementation

**WARP** (Writing As Reasoning Policy) is an iterative state-machine pipeline for
autonomous report generation. A Router agent repeatedly inspects progress and
dispatches to specialized agents until a complete report emerges.

## Architecture

```
User Query
    │
    ▼
┌──────────┐
│State Init│  ← WarpState (Pydantic model)
└────┬─────┘
     ▼
┌─────────────────────────────────┐
│  Router (PydanticAI Agent)      │◄──────────────┐
│  Inspects state, picks action   │               │
└────┬────┬────┬────┬────┬────────┘               │
     │    │    │    │    │                         │
     ▼    ▼    ▼    ▼    ▼                         │
  Search  Init Write Extend Done                   │
  (act)  (act) (act) (act) (act)                   │
     │    │    │    │    │                         │
     └────┴────┴────┴────┴─── state update ───────┘
```

Each box is a **Temporal Activity** wrapping a **PydanticAI Agent**.

## File Structure

| File | Purpose |
|------|---------|
| `models.py` | Pydantic state models (`WarpState`, `RouterDecision`, etc.) |
| `agents.py` | PydanticAI agents (Router, Search, Analyst, Writer, Formatter) |
| `activities.py` | Temporal activities wrapping each agent |
| `workflow.py` | Temporal workflow — the WARP loop with safety guards |
| `worker.py` | Temporal worker entry point |
| `client.py` | CLI client to trigger a WARP run |

## How It Works

1. **State Init**: `WarpState` is created from the user query
2. **Router Loop** (Temporal Workflow):
   - `route_action` activity asks the Router agent what to do next
   - Workflow dispatches to the matching activity (`search_passages`, `create_outline`, etc.)
   - Activity runs the PydanticAI agent, updates state, returns serialized JSON
   - Loop continues until Router says `DONE` or `max_iterations` is hit
3. **Safety Guards**:
   - Stuck detection (same action 3× in a row → force finish)
   - Max iteration cap (default: 10)
   - Temporal retry policies with exponential backoff on each activity

## Why Temporal + PydanticAI

| Concern | Temporal | PydanticAI |
|---------|----------|------------|
| Durable execution | ✅ Survives crashes | — |
| Retry/backoff | ✅ Per-activity policies | — |
| Observability | ✅ Full event history in UI | — |
| Structured output | — | ✅ `result_type` validation |
| Type safety | — | ✅ Pydantic models |
| LLM abstraction | — | ✅ Swap models easily |

## Quick Start

```bash
# 1. Start Temporal dev server
temporal server start-dev

# 2. Install deps
pip install temporalio pydantic-ai pydantic

# 3. Start worker
python worker.py

# 4. Run a query
python client.py "Impact of knowledge graphs on Industry 4.0"
