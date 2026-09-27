from typing import Literal
from pydantic import BaseModel, Field, field_validator

Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=120)
    user_id: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=13, le=120)
    weight: float = Field(gt=0, le=500)
    goal: Goal
    intensity: Intensity

    @field_validator("username", "user_id")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=80)
    feedback: str = Field(min_length=3, max_length=1000)

    @field_validator("user_id", "feedback")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class WorkoutResponse(BaseModel):
    user_id: str
    username: str
    goal: str
    intensity: str
    workout_plan: str
    nutrition_tip: str
    mode: str


class FeedbackResponse(BaseModel):
    user_id: str
    updated_plan: str
    nutrition_tip: str
    mode: str
