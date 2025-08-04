from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ExchangeRequest:
    """
    Modelo para la solicitud de cambio de divisas.
    """
    source_currency: str
    target_currency: str
    amount: float

    def __post_init__(self):
        """Validación básica de los datos de entrada."""
        if not isinstance(self.source_currency, str) or len(self.source_currency) != 3:
            raise ValueError("La moneda de origen debe ser un código de 3 letras")
        
        if not isinstance(self.target_currency, str) or len(self.target_currency) != 3:
            raise ValueError("La moneda de destino debe ser un código de 3 letras")
        
        if not isinstance(self.amount, (int, float)) or self.amount <= 0:
            raise ValueError("La cantidad debe ser un número positivo")
        
        # Convertir a mayúsculas los códigos de moneda
        self.source_currency = self.source_currency.upper()
        self.target_currency = self.target_currency.upper()


@dataclass
class ExchangeResponse:
    """
    Modelo para la respuesta de una API de cambio de divisas.
    """
    provider_name: str
    converted_amount: float
    rate: float
    response_time_ms: float
    success: bool
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class BestExchangeResult:
    """
    Modelo para el resultado final con la mejor oferta.
    """
    best_provider: str
    best_rate: float
    best_converted_amount: float
    source_currency: str
    target_currency: str
    original_amount: float
    total_providers_queried: int
    successful_providers: int
    failed_providers: int
    total_time_ms: float
