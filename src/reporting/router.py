"""
FastAPI router for the Reporting service.

Provides admin-only endpoints for the platform dashboard and CSV data exports.
All endpoints require the ``admin`` role via :func:`~src.auth.dependencies.require_admin`.

Endpoints
---------
- ``GET  /dashboard`` — aggregate platform statistics.
- ``POST /export``    — download a CSV report for the requested report type.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import require_admin
from src.database import get_db
from src.models import User
from src.reporting.schemas import (
    AdminDashboardResponse,
    CSVExportRequest,
    ReportType,
)
from src.reporting.service import (
    export_enrollments_csv,
    export_learner_progress_csv,
    get_admin_dashboard,
)
from src.sanitize import sanitize_log

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
    summary="Admin dashboard",
    description="Return aggregate platform statistics for the admin reporting view.",
)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> AdminDashboardResponse:
    """Return aggregate platform statistics for the admin reporting view.

    Includes total user, course, and enrollment counts, the overall completion
    rate, per-course enrollment breakdowns, and a top-learners list.

    Args:
        db: Async database session injected by FastAPI.
        current_user: The authenticated admin user (enforced by ``require_admin``).

    Returns:
        An :class:`~src.reporting.schemas.AdminDashboardResponse` containing
        all dashboard metrics.
    """
    logger.info("Admin dashboard requested by user=%s", current_user.id)
    return await get_admin_dashboard(db)


@router.post(
    "/export",
    summary="Export CSV report",
    description="Generate and download a CSV report for the specified report type.",
)
async def export_csv(
    body: CSVExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> Response:
    """Generate and return a CSV file for the requested report type.

    Supported report types:

    - ``enrollments`` — all enrollment records with user/course details.
    - ``learner_progress`` — per-learner completion summaries.
    - ``quiz_results`` — *not yet implemented* (returns HTTP 501).

    Args:
        body: A :class:`~src.reporting.schemas.CSVExportRequest` specifying
            which report to generate.
        db: Async database session injected by FastAPI.
        current_user: The authenticated admin user (enforced by ``require_admin``).

    Returns:
        A ``text/csv`` :class:`~fastapi.responses.Response` with a
        ``Content-Disposition`` header prompting a file download.

    Raises:
        :class:`~fastapi.HTTPException` (501) if the requested report type
            is not yet implemented.
    """
    logger.info(
        "CSV export requested: report_type=%s user=%s",
        sanitize_log(body.report_type.value),
        sanitize_log(current_user.id),
    )

    if body.report_type == ReportType.enrollments:
        csv_content: str = await export_enrollments_csv(db)
    elif body.report_type == ReportType.learner_progress:
        csv_content = await export_learner_progress_csv(db)
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Report type '{body.report_type.value}' is not implemented yet.",
        )

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="report.csv"',
        },
    )


__all__ = ["router"]
