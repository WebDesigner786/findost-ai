"""Dashboard Pydantic Schemas"""

from typing import List
from pydantic import BaseModel, ConfigDict
from app.schemas.workspace import WorkspaceOut
from app.schemas.transaction import TransactionOut
from app.schemas.forecast import ForecastOut
from app.schemas.anomaly import AnomalyOut


class DashboardKpis(BaseModel):
    netBalance: str  # exact paisa string
    runwayDays: int
    monthlyOutflow: str  # exact paisa string
    monthlyInflow: str  # exact paisa string
    totalOutstandingUdhaar: str  # exact paisa string
    overdueUdhaarCount: int

    model_config = ConfigDict(populate_by_name=True)


class DashboardData(BaseModel):
    workspace: WorkspaceOut
    kpis: DashboardKpis
    forecast: ForecastOut
    anomalies: List[AnomalyOut]
    recentTransactions: List[TransactionOut]
    freshnessTimestamp: str

    model_config = ConfigDict(populate_by_name=True)
