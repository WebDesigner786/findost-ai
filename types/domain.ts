export type WorkspaceKind = "student" | "household" | "sme" | "enterprise";

export interface Workspace {
  id: string;
  kind: WorkspaceKind;
  name: string;
  displayName: string;
  description: string;
  currency: "PKR";
  timezone: "Asia/Karachi";
  features: string[]; // e.g. ["cash_flow", "budgeting", "udhaar", "tax_estimate", "credit_readiness"]
}

export type Money = {
  currency: "PKR";
  amountPaisa: string; // integer string, exact (100 paisa = 1 PKR)
};

export interface Transaction {
  id: string;
  workspaceId: string;
  occurredAt: string; // YYYY-MM-DD
  merchant: string;
  amount: Money;
  direction: "inflow" | "outflow";
  category: string;
  confidence?: number; // 0.0 - 1.0 (e.g. 0.62 for low, 0.98 for high)
  reviewStatus: "confirmed" | "needs_review";
  sourceRef?: string; // Synthetic reference ID, e.g. "INV-2026-084", "RCP-BGS-112"
  // Audit trail for user corrections
  isEdited?: boolean;
  originalMerchant?: string;
  originalCategory?: string;
  originalAmount?: Money;
  correctionNote?: string;
}

export interface ForecastPoint {
  date: string; // YYYY-MM-DD
  baseline: Money;
  p10?: Money;
  p50?: Money;
  p90?: Money;
  simulated?: Money;
}

export interface Forecast {
  workspaceId: string;
  generatedAt: string;
  horizonDays: number;
  points: ForecastPoint[];
  assumptions: string[];
  source: "api" | "demo";
}

export interface UdhaarRecord {
  id: string;
  workspaceId: string;
  customerName: string;
  phone?: string;
  issuedAt: string;
  dueAt?: string;
  outstanding: Money;
  status: "current" | "overdue" | "settled";
  ageBucket: "30d" | "60d" | "90d+";
  sourceRef?: string;
  notes?: string;
}

export interface Anomaly {
  id: string;
  workspaceId: string;
  kind: "spike" | "duplicate" | "supplier_price" | "overdue_udhaar";
  severity: "info" | "warning" | "critical";
  title: string;
  explanation: string;
  amount?: Money;
  period: string;
  transactionIds: string[];
  sourceRefs: string[];
  detectedAt: string;
}

export interface ScenarioShock {
  id: string;
  kind: "price_rise" | "delayed_receivables" | "utility_spike" | "custom";
  label: string;
  description: string;
  percent?: number;
  delayDays?: number;
  amount?: Money;
  active: boolean;
}

export interface RecoveryAction {
  id: string;
  label: string;
  description: string;
  estimatedImpact: Money;
  active: boolean;
}

export interface Scenario {
  id: string;
  workspaceId: string;
  title: string;
  description: string;
  shocks: ScenarioShock[];
  recoveryActions: RecoveryAction[];
  assumptions: string[];
  simulatedShortageDate?: string | null;
}

export interface Recommendation {
  id: string;
  workspaceId: string;
  title: string;
  plainReason: string;
  estimatedImpact: Money;
  timeHorizon: string; // e.g. "Next 30 days"
  evidenceTransactionIds: string[];
  evidenceSourceRefs: string[];
  assumptions: string[];
  category: "cash_flow" | "supplier" | "collections" | "tax";
}

export interface CreditReadinessFactor {
  name: string;
  score: number; // 0 - 100
  weight: number;
  status: "good" | "moderate" | "attention";
  details: string;
}

export interface CreditReadiness {
  workspaceId: string;
  overallScore: number; // 0 - 100
  factors: CreditReadinessFactor[];
  isShariahCompliantWording: boolean;
  disclaimer: string;
}

export interface TaxDeductibleCategory {
  category: string;
  spent: Money;
  deductiblePercentage: number;
  deductibleAmount: Money;
  note: string;
}

export interface TaxPreview {
  workspaceId: string;
  taxYear: string;
  estimatedGrossInflow: Money;
  totalExpenses: Money;
  deductibleExpenses: Money;
  estimatedTaxableIncome: Money;
  illustrativeEstimatedTax: Money;
  deductibleCategories: TaxDeductibleCategory[];
  disclaimer: string;
}
