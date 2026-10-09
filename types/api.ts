import { Workspace, Transaction, Forecast, UdhaarRecord, Anomaly, Recommendation, CreditReadiness, TaxPreview } from "./domain";

export interface ApiResponse<T> {
  data: T;
  meta?: {
    source: "api" | "demo";
    timestamp: string;
    version?: string;
  };
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export interface DashboardData {
  workspace: Workspace;
  kpis: {
    netBalance: string; // paisa string
    runwayDays: number;
    monthlyOutflow: string; // paisa string
    monthlyInflow: string; // paisa string
    totalOutstandingUdhaar: string; // paisa string
    overdueUdhaarCount: number;
  };
  forecast: Forecast;
  anomalies: Anomaly[];
  recentTransactions: Transaction[];
  freshnessTimestamp: string;
}

export interface SettlementPayload {
  udhaarId: string;
  amountPaisa: string;
  notes?: string;
}

export interface ImportTransactionsPayload {
  transactions: Array<Omit<Transaction, "id">>;
}

export interface UpdateTransactionPayload {
  merchant?: string;
  category?: string;
  amountPaisa?: string;
  reviewStatus?: "confirmed" | "needs_review";
  correctionNote?: string;
}
