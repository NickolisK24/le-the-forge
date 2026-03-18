"""
Response helpers — enforce a consistent JSON envelope across all endpoints.

All API responses follow this shape:
{
    "data":   <payload or null>,
    "meta":   <pagination / extra context or null>,
    "errors": <list of error objects or null>
}
"""

from flask import jsonify
from marshmallow import ValidationError


def ok(data=None, meta=None, status=200):
    return jsonify({"data": data, "meta": meta, "errors": None}), status


def created(data=None):
    return ok(data=data, status=201)


def no_content():
    return "", 204


def error(message: str, status: int = 400, field: str = None):
    err = {"message": message}
    if field:
        err["field"] = field
    return jsonify({"data": None, "meta": None, "errors": [err]}), status


def validation_error(exc: ValidationError):
    errors = []
    for field_name, messages in exc.messages.items():
        for msg in (messages if isinstance(messages, list) else [messages]):
            errors.append({"field": field_name, "message": msg})
    return jsonify({"data": None, "meta": None, "errors": errors}), 422


def not_found(resource: str = "Resource"):
    return error(f"{resource} not found.", status=404)


def forbidden():
    return error("You don't have permission to do that.", status=403)


def unauthorized():
    return error("Authentication required.", status=401)


def paginate_meta(page: int, per_page: int, total: int, pages: int) -> dict:
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1,
    }
