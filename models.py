"""
WARP (Writing As Reasoning Policy) Loop - State Models
=======================================================
Pydantic models for the WARP pipeline state machine.
Each cycle: Router inspects state → picks action → action updates state → loop.
"""

from __future__ import annotations

from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class WarpAction(str, Enum):
    """Actions the Router can dispatch."""
    SEARCH = "search"
    ANALYST_INIT = "analyst_init"
    WRITE = "write"
    ANALYST_EXTEND = "analyst_extend"
    DONE = "done"


class Passage(BaseModel):
    """A retrieved passage from the search step."""
    source: str
    content: str
    relevance_score: float = 0.0


class OutlineSection(BaseModel):
    """A section in the report outline."""
    id: str
    title: str
    key_points: list[str] = Field(default_factory=list)
    subsections: list[OutlineSection] = Field(default_factory=list)
    depth: int = 0


class DraftedSection(BaseModel):
    """A written section of the report."""
    section_id: str
    title: str
    content: str
    revision: int = 1
    word_count: int = 0


class WarpState(BaseModel):
    """
    Complete state for the WARP pipeline.
    Passed through every Temporal activity and updated incrementally.
    """
    # Input
    query: str
    
    # Search state
    search_queries_used: list[str] = Field(default_factory=list)
    passages: list[Passage] = Field(default_factory=list)
    
    # Outline state
    outline: list[OutlineSection] = Field(default_factory=list)
    outline_version: int = 0
    
    # Writing state
    drafted_sections: list[DraftedSection] = Field(default_factory=list)
    
    # Control flow
    current_action: WarpAction | None = None
    action_history: list[str] = Field(default_factory=list)
    iteration: int = 0
    max_iterations: int = 10
    
    # Output
    final_report: str | None = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def has_outline(self) -> bool:
        return len(self.outline) > 0

    @property
    def has_passages(self) -> bool:
        return len(self.passages) > 0
    
    @property
    def sections_drafted(self) -> int:
        return len(self.drafted_sections)
    
    @property
    def sections_in_outline(self) -> int:
        return len(self.outline)
    
    @property
    def all_sections_drafted(self) -> bool:
        if not self.has_outline:
            return False
        outline_ids = {s.id for s in self.outline}
        drafted_ids = {s.section_id for s in self.drafted_sections}
        return outline_ids.issubset(drafted_ids)


class RouterDecision(BaseModel):
    """Output from the Router agent — which action to take next and why."""
    action: WarpAction
    reasoning: str
    search_query: str | None = None  # populated if action == SEARCH
    target_section_id: str | None = None  # populated if action == WRITE