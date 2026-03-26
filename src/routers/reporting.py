"""Reporting router — admin-only endpoints for dashboard, learner stats, and CSV export."""

import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.dependencies.rbac import require_admin
from src.services.reporting_service import get_dashboard_stats, get_learner_report, export_enrollments_csv
from src.schemas.reporting import DashboardResponse, LearnerReportRow

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    """Return aggregated admin dashboard statistics."""
    return await get_dashboard_stats(db)


@router.get("/learners", response_model=list[LearnerReportRow])
async def get_learner_stats(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    """Return per-learner enrollment and completion summary."""
    return await get_learner_report(db)


@router.get("/export/csv")
async def export_csv(
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    """Export all enrollment records as a CSV file download."""
    csv_content = await export_enrollments_csv(db)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=enrollments.csv"},
    )
