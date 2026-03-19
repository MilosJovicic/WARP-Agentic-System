"""
WARP Loop - PydanticAI Agents
==============================
Each agent handles one action branch in the WARP state machine.
Agents are stateless — all context comes from WarpState.
"""

from __future__ import annotations

from pydantic_ai import Agent

from models import (
    WarpState,
    RouterDecision,
    WarpAction,
    Passage,
    OutlineSection,
    DraftedSection,
)

# ---------------------------------------------------------------------------
# 1. Router Agent — the "brain" of the loop
# ---------------------------------------------------------------------------

router_agent = Agent(
    "anthropic:claude-sonnet-4-20250514",
    system_prompt=(
        "You are the Router in a WARP (Writing As Reasoning Policy) pipeline. "
        "Your job is to inspect the current state of a report-generation task "
        "and decide the NEXT action to take.\n\n"
        "Actions available:\n"
        "- search: Retrieve more passages when knowledge is insufficient.\n"
        "- analyst_init: Create an initial outline (only if no outline exists).\n"
        "- write: Draft a specific section from the outline.\n"
        "- analyst_extend: Deepen/refine the outline with new information.\n"
        "- done: Finalize when all sections are drafted and quality is sufficient.\n\n"
        "Rules:\n"
        "1. Always search FIRST if no passages exist.\n"
        "2. Create outline before writing.\n"
        "3. Write sections incrementally — one at a time.\n"
        "4. Use analyst_extend if new passages reveal gaps in the outline.\n"
        "5. Choose 'done' only when all outline sections have drafts.\n"
        "6. Provide clear reasoning for your choice."
    ),
    result_type=RouterDecision,
)


# ---------------------------------------------------------------------------
# 2. Search Agent — generates search queries and processes results
# ---------------------------------------------------------------------------

from pydantic import BaseModel as _BaseModel


class SearchQueries(_BaseModel):
    """1-3 search queries to fill knowledge gaps."""
    queries: list[str]


search_agent = Agent(
    "anthropic:claude-sonnet-4-20250514",
    system_prompt=(
        "You are the Search planner in a WARP pipeline. "
        "Given the user query, existing passages, and the current outline, "
        "generate 1-3 targeted search queries to fill knowledge gaps. "
        "Avoid duplicating previous search queries."
    ),
    result_type=SearchQueries,
)


# ---------------------------------------------------------------------------
# 3. Analyst-Init Agent — creates the initial outline
# ---------------------------------------------------------------------------

class OutlineResult(_BaseModel):
    sections: list[OutlineSection]


analyst_init_agent = Agent(
    "anthropic:claude-sonnet-4-20250514",
    system_prompt=(
        "You are the Analyst in a WARP pipeline. "
        "Given the user query and retrieved passages, create a structured "
        "report outline. Each section needs an id (e.g. 's1', 's2'), a title, "
        "and key points to cover. Keep it focused — 3-6 top-level sections."
    ),
    result_type=OutlineResult,
)


# ---------------------------------------------------------------------------
# 4. Write Agent — drafts a single section
# ---------------------------------------------------------------------------

class SectionDraft(_BaseModel):
    section_id: str
    title: str
    content: str
    word_count: int


write_agent = Agent(
    "anthropic:claude-sonnet-4-20250514",
    system_prompt=(
        "You are the Writer in a WARP pipeline. "
        "Given the user query, an outline section, and retrieved passages, "
        "write a well-structured section for the report. "
        "Use the passages as evidence. Be thorough but concise. "
        "Return the section_id, title, content, and word_count."
    ),
    result_type=SectionDraft,
)


# ---------------------------------------------------------------------------
# 5. Analyst-Extend Agent — deepens the outline
# ---------------------------------------------------------------------------

analyst_extend_agent = Agent(
    "anthropic:claude-sonnet-4-20250514",
    system_prompt=(
        "You are the Analyst-Extend in a WARP pipeline. "
        "Review the current outline against newly retrieved passages. "
        "Add subsections, refine key points, or insert new sections "
        "if the passages reveal important topics not yet covered. "
        "Return the updated full outline."
    ),
    result_type=OutlineResult,
)


# ---------------------------------------------------------------------------
# 6. Format Agent — assembles the final report
# ---------------------------------------------------------------------------

class FinalReport(_BaseModel):
    report: str


format_agent = Agent(
    "anthropic:claude-sonnet-4-20250514",
    system_prompt=(
        "You are the Formatter in a WARP pipeline. "
        "Given all drafted sections and the outline, assemble a polished "
        "final report. Add an executive summary, smooth transitions between "
        "sections, and a conclusion. Output clean Markdown."
    ),
    result_type=FinalReport,
)

