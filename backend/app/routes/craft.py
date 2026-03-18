"""
Craft Blueprint — /api/craft

POST   /api/craft                  → Create a new craft session
POST   /api/craft/predict          → Stateless optimal path + Monte Carlo (no session)
GET    /api/craft/<slug>           → Get session with step log
POST   /api/craft/<slug>/action    → Apply a forge action
GET    /api/craft/<slug>/summary   → Get session summary + optimal path + simulation
DELETE /api/craft/<slug>           → Delete session (owner only)

Sessions can be created without auth (anonymous simulation).
Auth is required only to persist and share sessions.
"""

from flask import Blueprint, request
from marshmallow import ValidationError

from app.models import CraftSession
from app.schemas import (
    CraftSessionSchema,
    CraftSessionCreateSchema,
    CraftActionSchema,
    CraftPredictSchema,
)
from app.services import craft_service
from app.utils.auth import get_current_user
from app.utils.responses import (
    ok, created, no_content, error,
    not_found, forbidden, validation_error,
)

craft_bp = Blueprint("craft", __name__)

session_schema = CraftSessionSchema()
session_create_schema = CraftSessionCreateSchema()
action_schema = CraftActionSchema()
predict_schema = CraftPredictSchema()


@craft_bp.post("")
def create_session():
    try:
        data = session_create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    user = get_current_user()
    session = craft_service.create_session(data, user_id=user.id if user else None)
    return created(data=session_schema.dump(session))


@craft_bp.post("/predict")
def predict():
    """
    Stateless crafting outcome predictor — no session required.
    Returns the optimal path, Monte Carlo simulation result, and
    a three-strategy comparison for the given item state.
    """
    try:
        data = predict_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    instability = data["instability"]
    forge_potential = data["forge_potential"]
    affixes = data.get("affixes", [])
    n_simulations = data.get("n_simulations", 10_000)

    path = craft_service.optimal_path_search(instability, affixes, forge_potential)

    sim_steps = [
        {"action": s["action"], "sealed_count_at_step": s["sealed_count_at_step"]}
        for s in path
    ]
    sim_result = craft_service.simulate_sequence(
        instability, forge_potential, sim_steps, n_simulations
    ) if sim_steps else {
        "brick_chance": 0.0,
        "perfect_item_chance": 1.0,
        "step_survival_curve": [],
        "step_fracture_rates": [],
        "median_instability": instability,
        "n_simulations": 0,
    }

    strategies = craft_service.compare_strategies(instability, affixes, forge_potential)

    return ok(data={
        "optimal_path": path,
        "simulation_result": sim_result,
        "strategy_comparison": strategies,
    })


@craft_bp.get("/<slug>")
def get_session(slug: str):
    session = CraftSession.query.filter_by(slug=slug).first()
    if not session:
        return not_found("Craft session")

    # If session has an owner, only the owner can view it
    if session.user_id:
        user = get_current_user()
        if not user or session.user_id != user.id:
            return forbidden()

    return ok(data=session_schema.dump(session))


@craft_bp.post("/<slug>/action")
def apply_action(slug: str):
    session = CraftSession.query.filter_by(slug=slug).first()
    if not session:
        return not_found("Craft session")

    # If session has an owner, only the owner can modify it
    if session.user_id:
        user = get_current_user()
        if not user or session.user_id != user.id:
            return forbidden()

    try:
        data = action_schema.load(request.get_json() or {})
    except ValidationError as e:
        return validation_error(e)

    result = craft_service.apply_action(
        session,
        action=data["action"],
        affix_name=data.get("affix_name"),
        target_tier=data.get("target_tier"),
    )

    return ok(data=result)


@craft_bp.get("/<slug>/summary")
def get_summary(slug: str):
    session = CraftSession.query.filter_by(slug=slug).first()
    if not session:
        return not_found("Craft session")
    return ok(data=craft_service.get_session_summary(session))


@craft_bp.delete("/<slug>")
def delete_session(slug: str):
    session = CraftSession.query.filter_by(slug=slug).first()
    if not session:
        return not_found("Craft session")

    user = get_current_user()
    if session.user_id and (not user or session.user_id != user.id):
        return forbidden()

    from app import db
    db.session.delete(session)
    db.session.commit()
    return no_content()
