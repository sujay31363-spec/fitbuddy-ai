from fastapi import (
    APIRouter,
    Request,
    Form,
    HTTPException
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import Jinja2Templates

from .schemas import (
    UserInput,
    FeedbackRequest
)

from .database import (
    save_user,
    save_plan,
    get_user,
    get_latest_plan,
    update_plan,
    get_all_users,
    delete_user
)

from .ai import (
    generate_workout_gemini,
    generate_nutrition_tip_with_flash,
    update_workout_plan,
    demo_workout,
    demo_tip
)

from .config import get_settings


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)

settings = get_settings()


def ai_call(
    function,
    fallback
):

    try:

        return function()

    except Exception as error:

        print(
            "AI Error:",
            error
        )

        return fallback()


@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={
            "title": "FitBuddy"
        }
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(

    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...)
):

    try:

        data = UserInput(

            username=username,

            user_id=user_id,

            age=age,

            weight=weight,

            goal=goal,

            intensity=intensity
        )

    except Exception as error:

        return templates.TemplateResponse(

            request=request,

            name="index.html",

            context={
                "title": "FitBuddy",
                "error": str(error)
            },

            status_code=422
        )


    workout_plan = ai_call(

        lambda: generate_workout_gemini(

            data.username,

            data.age,

            data.weight,

            data.goal,

            data.intensity
        ),

        lambda: demo_workout(

            data.goal,

            data.intensity
        )
    )


    nutrition_tip = ai_call(

        lambda: generate_nutrition_tip_with_flash(

            data.goal
        ),

        lambda: demo_tip(

            data.goal
        )
    )


    user = save_user(
        data.model_dump()
    )


    plan = save_plan(

        user.id,

        workout_plan,

        nutrition_tip
    )


    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context={

            "title": "Your FitBuddy Plan",

            "user": user,

            "plan": plan,

            "is_demo":
                not settings.gemini_api_key
                or not settings.ai_enabled
        }
    )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...)
):

    try:

        data = FeedbackRequest(

            user_id=user_id,

            feedback=feedback
        )

    except Exception as error:

        raise HTTPException(

            status_code=422,

            detail=str(error)
        )


    user = get_user(
        data.user_id
    )

    plan = get_latest_plan(
        data.user_id
    )


    if not user or not plan:

        raise HTTPException(

            status_code=404,

            detail="User or plan not found"
        )


    revised_plan = ai_call(

        lambda: update_workout_plan(

            plan.original_plan,

            data.feedback,

            user.goal,

            user.intensity
        ),

        lambda:
            plan.original_plan
            + "\n\n[Demo update]\nFeedback received: "
            + data.feedback
    )


    updated_plan = update_plan(

        plan.id,

        revised_plan,

        data.feedback
    )


    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context={

            "title": "Updated FitBuddy Plan",

            "user": user,

            "plan": updated_plan,

            "message":
                "Your plan was updated successfully.",

            "is_demo":
                not settings.gemini_api_key
                or not settings.ai_enabled
        }
    )


# -----------------------------
# ADMIN
# -----------------------------


@router.get(
    "/admin",
    response_class=HTMLResponse
)
def admin_page(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="admin_login.html",

        context={
            "title": "FitBuddy Admin"
        }
    )


@router.post(
    "/admin/login",
    response_class=HTMLResponse
)
def admin_login(

    request: Request,

    username: str = Form(...),

    password: str = Form(...)
):

    if (

        username !=
        settings.admin_username

        or

        password !=
        settings.admin_password

    ):

        return templates.TemplateResponse(

            request=request,

            name="admin_login.html",

            context={

                "title": "FitBuddy Admin",

                "error":
                    "Invalid username or password."
            },

            status_code=401
        )


    return RedirectResponse(

        url="/view-all-users",

        status_code=303
    )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(
    request: Request
):

    users = get_all_users()

    rows = []


    for user in users:

        plan = get_latest_plan(
            user.user_id
        )

        rows.append({

            "user": user,

            "plan": plan
        })


    return templates.TemplateResponse(

        request=request,

        name="all_users.html",

        context={

            "title": "All Users",

            "rows": rows
        }
    )


@router.post(
    "/admin/delete/{user_id}"
)
def admin_delete(
    user_id: str
):

    delete_user(
        user_id
    )

    return RedirectResponse(

        url="/view-all-users",

        status_code=303
    )


# -----------------------------
# API
# -----------------------------


@router.get(
    "/api/health"
)
def health():

    return {

        "status": "ok",

        "service": "FitBuddy",

        "ai_configured":
            bool(
                settings.gemini_api_key
                and settings.ai_enabled
            )
    }


@router.post(
    "/api/generate"
)
def api_generate(
    data: UserInput
):

    workout_plan = ai_call(

        lambda:
            generate_workout_gemini(
                **data.model_dump()
            ),

        lambda:
            demo_workout(
                data.goal,
                data.intensity
            )
    )


    nutrition_tip = ai_call(

        lambda:
            generate_nutrition_tip_with_flash(
                data.goal
            ),

        lambda:
            demo_tip(
                data.goal
            )
    )


    user = save_user(
        data.model_dump()
    )


    plan = save_plan(

        user.id,

        workout_plan,

        nutrition_tip
    )


    return {

        "user_id":
            user.user_id,

        "plan_id":
            plan.id,

        "workout_plan":
            workout_plan,

        "nutrition_tip":
            nutrition_tip
    }


@router.post(
    "/api/feedback"
)
def api_feedback(
    data: FeedbackRequest
):

    user = get_user(
        data.user_id
    )

    plan = get_latest_plan(
        data.user_id
    )


    if not user or not plan:

        raise HTTPException(

            status_code=404,

            detail="User or plan not found"
        )


    revised_plan = ai_call(

        lambda:
            update_workout_plan(

                plan.original_plan,

                data.feedback,

                user.goal,

                user.intensity
            ),

        lambda:
            plan.original_plan
            + "\n\n[Demo update]\nFeedback received: "
            + data.feedback
    )


    updated = update_plan(

        plan.id,

        revised_plan,

        data.feedback
    )


    return {

        "user_id":
            user.user_id,

        "plan_id":
            updated.id,

        "updated_plan":
            updated.updated_plan
    }


@router.get(
    "/api/users"
)
def api_users():

    users = get_all_users()


    return [

        {

            "user_id":
                user.user_id,

            "username":
                user.username,

            "age":
                user.age,

            "weight":
                user.weight,

            "goal":
                user.goal,

            "intensity":
                user.intensity
        }

        for user in users
    ]


@router.get(
    "/api/users/{user_id}"
)
def api_user(
    user_id: str
):

    user = get_user(
        user_id
    )

    plan = get_latest_plan(
        user_id
    )


    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"
        )


    return {

        "user_id":
            user.user_id,

        "username":
            user.username,

        "age":
            user.age,

        "weight":
            user.weight,

        "goal":
            user.goal,

        "intensity":
            user.intensity,

        "original_plan":
            plan.original_plan
            if plan else None,

        "updated_plan":
            plan.updated_plan
            if plan else None,

        "nutrition_tip":
            plan.nutrition_tip
            if plan else None
    }