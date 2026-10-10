"""Common Schemas & Exact Money Type Converter

Ensures 100% interoperability between backend Decimal/NUMERIC(14,2)
and frontend Money object with exact integer paisa strings.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Generic, Optional, TypeVar, Any
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


def decimal_to_paisa_string(amount_decimal: Decimal) -> str:
    """Converts a Decimal amount (e.g. Decimal('420000.00')) to exact integer paisa string ('42000000')."""
    if amount_decimal is None:
        return "0"
    paisa = (amount_decimal * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return str(int(paisa))


def paisa_string_to_decimal(paisa_str: str) -> Decimal:
    """Converts an integer paisa string (e.g. '42000000') to exact Decimal ('420000.00')."""
    if not paisa_str or not paisa_str.strip():
        return Decimal("0.00")
    clean = paisa_str.strip().replace(",", "")
    paisa_int = int(clean)
    return (Decimal(paisa_int) / Decimal("100")).quantize(Decimal("0.01"))


class Money(BaseModel):
    """Exact Money representation matching frontend domain contract."""
    currency: str = "PKR"
    amountPaisa: str = Field(..., description="Exact integer paisa string (1 PKR = 100 Paisa)")

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_decimal(cls, val: Decimal) -> "Money":
        return cls(currency="PKR", amountPaisa=decimal_to_paisa_string(val))

    def to_decimal(self) -> Decimal:
        return paisa_string_to_decimal(self.amountPaisa)


class ApiErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ApiErrorResponse(BaseModel):
    error: ApiErrorDetail


class ApiResponseMeta(BaseModel):
    source: str = "api"
    timestamp: str
    version: Optional[str] = "1.0.0"


class ApiResponse(BaseModel, Generic[T]):
    data: T
    meta: Optional[ApiResponseMeta] = None
