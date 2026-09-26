from google import genai
from google.genai import types

from .config import get_settings


settings = get_settings()

_client = None


def get_client():

    global _client

    if not settings.ai_enabled:
        return None

    if not settings.gemini_api_key:
        return None

    if _client is None:

        _client = genai.Client(
            api_key=settings.gemini_api_key
        )

    return _client


def generate_with_gemini(
    model,
    prompt,
    max_tokens=5000
):

    client = get_client()

    if client is None:

        raise RuntimeError(
            "Gemini is not configured"
        )

    response = client.models.generate_content(

        model=model,

        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=0.7,

            max_output_tokens=max_tokens
        )
    )

    text = (
        response.text or ""
    ).strip()

    if not text:

        raise RuntimeError(
            "Gemini returned empty response"
        )

    return text


def generate_workout_gemini(
    username,
    age,
    weight,
    goal,
    intensity
):

    prompt = f"""
You are FitBuddy, a responsible AI fitness planning assistant.

Create a practical personalized 7-day general wellness workout plan.

USER INFORMATION

Name: {username}

Age: {age}

Weight: {weight} kg

Goal: {goal}

Workout intensity: {intensity}

IMPORTANT REQUIREMENTS:

1. Create exactly seven days.
2. Use headings Day 1 through Day 7.
3. Include at least one recovery/rest day.
4. Every day must contain:
   - Focus
   - Warm-up
   - Main workout
   - Rest guidance
   - Cooldown/recovery
5. Give exercises with sets/repetitions or duration.
6. Keep recommendations conservative and practical.
7. Do not diagnose diseases.
8. Do not prescribe medical treatment.
9. Do not promise guaranteed weight loss or muscle gain.

Return only the workout plan.
"""

    return generate_with_gemini(
        settings.gemini_plan_model,
        prompt
    )


def generate_nutrition_tip_with_flash(goal):

    prompt = f"""
You are FitBuddy.

Give one practical nutrition or recovery tip for someone
whose fitness goal is:

{goal}

Rules:

- 3 to 5 sentences.
- Simple language.
- No extreme dieting.
- No medical diagnosis.
- No medical treatment.
- No supplement prescription.
"""

    return generate_with_gemini(
        settings.gemini_tip_model,
        prompt,
        500
    )


def update_workout_plan(
    original_plan,
    feedback,
    goal,
    intensity
):

    prompt = f"""
You are FitBuddy.

Revise this existing 7-day fitness plan based on user feedback.

Fitness goal:
{goal}

Workout intensity:
{intensity}

ORIGINAL PLAN:

{original_plan}

USER FEEDBACK:

{feedback}

Create a revised 7-day plan.

Requirements:

- Day 1 through Day 7
- Focus
- Warm-up
- Main workout
- Rest guidance
- Cooldown/recovery
- Apply the user's feedback
- Maintain safe general wellness guidance
- Do not diagnose
- Do not prescribe medical treatment
"""

    return generate_with_gemini(
        settings.gemini_plan_model,
        prompt
    )


def demo_workout(
    goal,
    intensity
):

    return f"""
Day 1 — Full Body

Focus:
Foundational strength ({intensity} intensity)

Warm-up:
5-10 minutes brisk walking and mobility.

Main workout:
Squats 3 x 10
Incline push-ups 3 x 8
Glute bridges 3 x 12
Plank 3 x 20-30 seconds

Rest:
60-90 seconds between sets.

Cooldown:
5 minutes easy walking and gentle stretching.


Day 2 — Cardio

Focus:
Goal-supportive cardio.

Warm-up:
5 minutes easy walking.

Main workout:
Brisk walk or cycling for 25-35 minutes.

Rest:
Keep the effort comfortable.

Cooldown:
5-10 minutes easy pace.


Day 3 — Upper Body and Core

Focus:
Upper-body strength.

Warm-up:
Shoulder circles and easy movement.

Main workout:
Incline push-ups 3 x 8-12
Rows 3 x 10
Dead bug 3 x 8 each side
Plank 3 x 20 seconds

Rest:
60-90 seconds.

Cooldown:
Gentle upper-body stretching.


Day 4 — Recovery

Focus:
Recovery and mobility.

Warm-up:
5-minute easy walk.

Main workout:
20-30 minute relaxed walk
plus gentle mobility exercises.

Rest:
Keep the effort easy.

Cooldown:
Slow breathing and stretching.


Day 5 — Lower Body

Focus:
Legs and hips.

Warm-up:
5-10 minute walk.

Main workout:
Squats 3 x 10
Reverse lunges 2 x 8 each side
Calf raises 3 x 12
Glute bridges 3 x 12

Rest:
60-90 seconds.

Cooldown:
Gentle lower-body stretching.


Day 6 — Cardio + Core

Focus:
Conditioning.

Warm-up:
5 minutes easy movement.

Main workout:
20-30 minute brisk cardio
Bird-dog 3 x 8 each side
Side plank 2 x 15-20 seconds

Rest:
Rest as needed.

Cooldown:
5 minutes easy movement.


Day 7 — Rest / Light Activity

Focus:
Recovery.

Warm-up:
Optional 5-minute easy walk.

Main workout:
Rest or easy 15-20 minute walk.

Rest:
Full recovery.

Cooldown:
Gentle stretching.


Goal:
{goal}

This is a local demo plan because Gemini is not configured.
"""


def demo_tip(goal):

    return f"""
For your {goal} goal, try to build meals around vegetables
or fruit, a protein source, whole-food carbohydrates and
adequate water.

Keep your recovery and sleep routine consistent and avoid
making extreme changes all at once.
"""