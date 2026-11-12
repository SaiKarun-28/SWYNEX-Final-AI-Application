"""Pydantic schema for the Smart Task Parser.

Single source of truth: the JSON schema sent to the LLM is derived from
`Task.model_json_schema()`, so the validator and the API contract can never
drift apart.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    Personal = "Personal"
    Work = "Work"
    Shopping = "Shopping"
    Errands = "Errands"
    Finance = "Finance"
    Health = "Health"
    Social = "Social"
    Home = "Home"
    Other = "Other"


class Priority(str, Enum):
    High = "High"
    Medium = "Medium"
    Low = "Low"


class Task(BaseModel):
    task_description: str = Field(
        ...,
        description="Refined, de-noised core task in the user's own words.",
    )
    category: Category = Field(
        ...,
        description="Best single category from the Category enum.",
    )
    priority: Priority = Field(
        ...,
        description="Inferred priority: High, Medium, or Low.",
    )
    deadline: Optional[str] = Field(
        default=None,
        description="ISO 8601 date or datetime if a time expression is present, else null.",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Model's self-reported confidence in category+priority, 0-1.",
    )
    is_ambiguous: bool = Field(
        default=False,
        description="True when confidence is below the ambiguity threshold.",
    )
