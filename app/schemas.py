from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):

    username: str = Field(
        min_length=2,
        max_length=120
    )

    user_id: str = Field(
        min_length=2,
        max_length=80
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight: float = Field(
        gt=20,
        lt=400
    )

    goal: str = Field(
        min_length=2,
        max_length=80
    )

    intensity: str

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, value):

        value = value.lower().strip()

        if value not in {
            "low",
            "medium",
            "high"
        }:

            raise ValueError(
                "Intensity must be low, medium, or high"
            )

        return value


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=80
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000
    )