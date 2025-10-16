from dataclasses import dataclass
from datetime import date
from .currency_codes import VALID_CURRENCY_CODES
from .trade_direction import TradeDirection
from .trade_style import TradeStyle

from trading_approval_process.domain.exceptions import ValidationException


@dataclass(frozen=True)
class TradeDetails:
    trading_entity: str
    counterparty: str
    direction: TradeDirection
    style: TradeStyle
    notional_currency: str
    notional_amount: float
    underlying: str
    trade_date: date
    value_date: date
    delivery_date: date
    strike: float | None = None
    confirmation_id: str | None = None


    def validate(self):
        if not self.trading_entity:
            raise ValidationException("TradingEntity is required")
        if not self.counterparty:
            raise ValidationException("Counterparty is required")
        if not self.notional_currency:
            raise ValidationException("NotionalCurrency is required")
        if self.notional_currency.upper() not in VALID_CURRENCY_CODES:
            raise ValidationException(f"Unsupported currency code: {self.notional_currency}")
        if self.notional_amount <= 0:
            raise ValidationException("NotionalAmount must be positive")
        if not self.underlying:
            raise ValidationException("Underlying is required")
        if self.notional_currency not in self.underlying:
            raise ValidationException("Underlying must include NotionalCurrency")
        if self.trade_date > self.value_date:
            raise ValidationException("TradeDate must be ≤ ValueDate")
        if self.value_date > self.delivery_date:
            raise ValidationException("ValueDate must be ≤ DeliveryDate")
