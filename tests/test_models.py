import pytest
from src.models.exchange_models import ExchangeRequest, ExchangeResponse, BestExchangeResult


class TestExchangeRequest:
    """Pruebas para el modelo ExchangeRequest."""
    
    def test_valid_request(self):
        """Prueba la creación de una solicitud válida."""
        request = ExchangeRequest(source_currency="USD", target_currency="EUR", amount=1000)
        assert request.source_currency == "USD"
        assert request.target_currency == "EUR"
        assert request.amount == 1000
    
    def test_currency_code_normalization(self):
        """Prueba la normalización de códigos de moneda a mayúsculas."""
        request = ExchangeRequest(source_currency="usd", target_currency="eur", amount=1000)
        assert request.source_currency == "USD"
        assert request.target_currency == "EUR"
    
    def test_invalid_source_currency(self):
        """Prueba la validación de moneda de origen inválida."""
        with pytest.raises(ValueError) as excinfo:
            ExchangeRequest(source_currency="USDD", target_currency="EUR", amount=1000)
        assert "moneda de origen" in str(excinfo.value).lower()
    
    def test_invalid_target_currency(self):
        """Prueba la validación de moneda de destino inválida."""
        with pytest.raises(ValueError) as excinfo:
            ExchangeRequest(source_currency="USD", target_currency="EURR", amount=1000)
        assert "moneda de destino" in str(excinfo.value).lower()
    
    def test_invalid_amount_negative(self):
        """Prueba la validación de cantidad negativa."""
        with pytest.raises(ValueError) as excinfo:
            ExchangeRequest(source_currency="USD", target_currency="EUR", amount=-100)
        assert "cantidad" in str(excinfo.value).lower()
    
    def test_invalid_amount_zero(self):
        """Prueba la validación de cantidad cero."""
        with pytest.raises(ValueError) as excinfo:
            ExchangeRequest(source_currency="USD", target_currency="EUR", amount=0)
        assert "cantidad" in str(excinfo.value).lower()
    
    def test_invalid_amount_type(self):
        """Prueba la validación de tipo de cantidad inválido."""
        with pytest.raises(ValueError) as excinfo:
            ExchangeRequest(source_currency="USD", target_currency="EUR", amount="1000")
        assert "cantidad" in str(excinfo.value).lower()


class TestExchangeResponse:
    """Pruebas para el modelo ExchangeResponse."""
    
    def test_successful_response(self):
        """Prueba la creación de una respuesta exitosa."""
        response = ExchangeResponse(
            provider_name="TestAPI",
            converted_amount=850.0,
            rate=0.85,
            response_time_ms=200.0,
            success=True,
            raw_response={"rate": 0.85}
        )
        assert response.provider_name == "TestAPI"
        assert response.converted_amount == 850.0
        assert response.rate == 0.85
        assert response.response_time_ms == 200.0
        assert response.success is True
        assert response.error_message is None
        assert response.raw_response == {"rate": 0.85}
    
    def test_error_response(self):
        """Prueba la creación de una respuesta con error."""
        response = ExchangeResponse(
            provider_name="TestAPI",
            converted_amount=0.0,
            rate=0.0,
            response_time_ms=200.0,
            success=False,
            error_message="API error",
            raw_response=None
        )
        assert response.provider_name == "TestAPI"
        assert response.converted_amount == 0.0
        assert response.rate == 0.0
        assert response.response_time_ms == 200.0
        assert response.success is False
        assert response.error_message == "API error"
        assert response.raw_response is None


class TestBestExchangeResult:
    """Pruebas para el modelo BestExchangeResult."""
    
    def test_best_result(self):
        """Prueba la creación de un resultado con la mejor oferta."""
        result = BestExchangeResult(
            best_provider="TestAPI",
            best_rate=0.85,
            best_converted_amount=850.0,
            source_currency="USD",
            target_currency="EUR",
            original_amount=1000.0,
            total_providers_queried=3,
            successful_providers=2,
            failed_providers=1,
            total_time_ms=500.0
        )
        assert result.best_provider == "TestAPI"
        assert result.best_rate == 0.85
        assert result.best_converted_amount == 850.0
        assert result.source_currency == "USD"
        assert result.target_currency == "EUR"
        assert result.original_amount == 1000.0
        assert result.total_providers_queried == 3
        assert result.successful_providers == 2
        assert result.failed_providers == 1
        assert result.total_time_ms == 500.0
