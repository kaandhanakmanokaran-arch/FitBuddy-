from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import Plan, User
from .schemas import FeedbackRequest, FeedbackResponse, UserInput, WorkoutResponse
from .services.gemini_flash_generator import generate_nutrition_tip_with_flash
from .services.gemini_generator import generate_workout_gemini
from .services.updated_plan import update_workout_plan

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
settings = get_settings()


def upsert_user(db: Session, data: UserInput) -> User:
    user = db.scalar(select(User).where(User.user_id == data.user_id))
    if user is None:
        user = User(
            user_id=data.user_id,
            username=data.username,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )
        db.add(user)
        db.flush()
    else:
        user.username = data.username
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity
    return user


def require_admin_token(token: str | None) -> None:
    if settings.admin_token and token != settings.admin_token:
        raise HTTPException(status_code=403, detail="Invalid admin token.")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "demo_mode": not settings.gemini_enabled})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_form(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        user = upsert_user(db, data)
        plan_text, mode = generate_workout_gemini(user)
        tip, tip_mode = generate_nutrition_tip_with_flash(user)
        plan = Plan(
            user_id=user.id,
            original_plan=plan_text,
            nutrition_tip=tip,
        )
        db.add(plan)
        db.commit()
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": plan,
                "display_plan": plan_text,
                "nutrition_tip": tip,
                "mode": "gemini" if mode == "gemini" or tip_mode == "gemini" else "demo",
            },
        )
    except ValueError as exc:
        db.rollback()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": str(exc)},
            status_code=422,
        )
    except Exception as exc:
        db.rollback()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request, "message": f"Could not generate the plan: {exc}"},
            status_code=500,
        )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_form(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = db.scalar(select(User).where(User.user_id == data.user_id))
        if user is None:
            raise ValueError("User ID was not found.")
        plan = db.scalar(
            select(Plan).where(Plan.user_id == user.id).order_by(Plan.created_at.desc())
        )
        if plan is None:
            raise ValueError("No workout plan exists for this user.")
        base_plan = plan.updated_plan or plan.original_plan
        updated, mode = update_workout_plan(user, base_plan, data.feedback)
        plan.updated_plan = updated
        plan.feedback = data.feedback
        plan.updated_at = datetime.utcnow()
        db.commit()
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "request": request,
                "user": user,
                "plan": plan,
                "display_plan": updated,
                "nutrition_tip": plan.nutrition_tip,
                "mode": mode,
                "message": "Your plan was updated successfully.",
            },
        )
    except ValueError as exc:
        db.rollback()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request, "message": str(exc)}, status_code=422)
    except Exception as exc:
        db.rollback()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request, "message": f"Could not update the plan: {exc}"}, status_code=500)


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request, admin_token: str | None = None, db: Session = Depends(get_db)):
    require_admin_token(admin_token)
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"request": request, "users": users, "admin_token": admin_token},
    )


@router.get("/api/health")
def health():
    return {"status": "ok", "service": settings.app_name, "gemini_enabled": settings.gemini_enabled}


@router.post("/api/workout", response_model=WorkoutResponse)
def api_generate_workout(data: UserInput, db: Session = Depends(get_db)):
    try:
        user = upsert_user(db, data)
        workout, mode = generate_workout_gemini(user)
        tip, tip_mode = generate_nutrition_tip_with_flash(user)
        plan = Plan(user_id=user.id, original_plan=workout, nutrition_tip=tip)
        db.add(plan)
        db.commit()
        return WorkoutResponse(
            user_id=user.user_id,
            username=user.username,
            goal=user.goal,
            intensity=user.intensity,
            workout_plan=workout,
            nutrition_tip=tip,
            mode="gemini" if "gemini" in (mode, tip_mode) else "demo",
        )
    except Exception:
        db.rollback()
        raise


@router.post("/api/feedback", response_model=FeedbackResponse)
def api_feedback(data: FeedbackRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.user_id == data.user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User ID was not found.")
    plan = db.scalar(select(Plan).where(Plan.user_id == user.id).order_by(Plan.created_at.desc()))
    if plan is None:
        raise HTTPException(status_code=404, detail="No workout plan exists for this user.")
    base_plan = plan.updated_plan or plan.original_plan
    updated, mode = update_workout_plan(user, base_plan, data.feedback)
    plan.updated_plan = updated
    plan.feedback = data.feedback
    plan.updated_at = datetime.utcnow()
    db.commit()
    return FeedbackResponse(
        user_id=user.user_id,
        updated_plan=updated,
        nutrition_tip=plan.nutrition_tip,
        mode=mode,
    )


@router.get("/api/tip/{goal}")
def api_tip(goal: str):
    allowed = {"weight loss", "muscle gain", "general wellness", "flexibility"}
    if goal not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported goal.")
    # A minimal object is enough for the tip service.
    from types import SimpleNamespace
    tip, mode = generate_nutrition_tip_with_flash(
        SimpleNamespace(age=18, goal=goal)
    )
    return {"goal": goal, "nutrition_tip": tip, "mode": mode}
