"""
Jobs Blueprint — /api/jobs

GET /api/jobs/<job_id>  → Poll status of a background job

Response shapes
---------------
Pending / running:
  {"data": {"id": "a1b2c3", "status": "pending"|"running", ...}, "errors": null}

Done:
  {"data": {"id": "a1b2c3", "status": "done", "result": {...}, ...}, "errors": null}

Error:
  {"data": {"id": "a1b2c3", "status": "error", "error": "...", ...}, "errors": null}

Not found:
  {"data": null, "errors": [{"message": "Job not found."}]}, 404
"""

from flask import Blueprint

from app.utils import jobs as job_store
from app.utils.responses import ok, not_found

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.get("/<job_id>")
def get_job(job_id: str):
    """Return current status of a background job."""
    status = job_store.get_status(job_id)
    if status is None:
        return not_found("Job")
    return ok(data=status)
