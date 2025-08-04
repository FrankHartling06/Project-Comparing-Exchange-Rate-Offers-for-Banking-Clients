import pytest
import asyncio
from unittest.mock import MagicMock, patch

from src.models.exchange_models import ExchangeRequest, ExchangeResponse
from src.interfaces.exchange_api_interface import ExchangeAPIInterface
from src.services.exchange_service import ExchangeService


class MockAPI(ExchangeAPIInterface):
    """API mock para pruebas."""
    
    def __init__(self, name, rate, response_time_ms, success=True, error_message=None):
        super().__init__()
        self.name = name
        self.rate = rate
        self.response_time_ms = response_time_ms
        self.should_succeed = success
        self.error_message = error_message
    
    async def get_exchange_rate(self, request):
        if not self.should_succeed:
            return self._create_error_response(request, self.error_message, self.response_time_ms)
        
        converted_amount = request.amount * self.rate
        return ExchangeResponse(
            provider_name=self.name,
            converted_amount=converted_amount,
            rate=self.rate,
            response_time_ms=self.response_time_ms,
            success=True,
            raw_response={"rate": self.rate}
        )
    
    def _prepare_request_data(self, request):
        return {}
    
    def _parse_response(self, response_data, request):
        pass


class TestExchangeService:
    """Pruebas para el servicio ExchangeService."""
    
    @pytest.fixture
    def exchange_request(self):
        """Fixture para crear una solicitud de prueba."""
        return ExchangeRequest(source_currency="USD", target_currency="EUR", amount=1000)
    
    @pytest.mark.asyncio
    async def test_get_best_exchange_rate_all_success(self, exchange_request):
        """Prueba obtener la mejor tasa cuando todas las APIs tienen éxito."""
        # Crear APIs mock con diferentes tasas
        api1 = MockAPI("API1", 0.85, 200)
        api2 = MockAPI("API2", 0.86, 300)  # Mejor tasa
        api3 = MockAPI("API3", 0.84, 250)
        
        # Crear servicio con las APIs mock
        service = ExchangeService([api1, api2, api3])
        
        # Obtener la mejor tasa
        result = await service.get_best_exchange_rate(exchange_request)
        
        # Verificar que se seleccionó la mejor tasa
        assert result.best_provider == "API2"
        assert result.best_rate == 0.86
        assert result.best_converted_amount == 860.0
        assert result.total_providers_queried == 3
        assert result.successful_providers == 3
        assert result.failed_providers == 0
    
    @pytest.mark.asyncio
    async def test_get_best_exchange_rate_some_failures(self, exchange_request):
        """Prueba obtener la mejor tasa cuando algunas APIs fallan."""
        # Crear APIs mock con diferentes tasas y una que falla
        api1 = MockAPI("API1", 0.85, 200)
        api2 = MockAPI("API2", 0.0, 300, success=False, error_message="Error simulado")
        api3 = MockAPI("API3", 0.84, 250)
        
        # Crear servicio con las APIs mock
        service = ExchangeService([api1, api2, api3])
        
        # Obtener la mejor tasa
        result = await service.get_best_exchange_rate(exchange_request)
        
        # Verificar que se seleccionó la mejor tasa entre las APIs exitosas
        assert result.best_provider == "API1"
        assert result.best_rate == 0.85
        assert result.best_converted_amount == 850.0
        assert result.total_providers_queried == 3
        assert result.successful_providers == 2
        assert result.failed_providers == 1
    
    @pytest.mark.asyncio
    async def test_get_best_exchange_rate_all_failures(self, exchange_request):
        """Prueba obtener la mejor tasa cuando todas las APIs fallan."""
        # Crear APIs mock que fallan
        api1 = MockAPI("API1", 0.0, 200, success=False, error_message="Error 1")
        api2 = MockAPI("API2", 0.0, 300, success=False, error_message="Error 2")
        api3 = MockAPI("API3", 0.0, 250, success=False, error_message="Error 3")
        
        # Crear servicio con las APIs mock
        service = ExchangeService([api1, api2, api3])
        
        # Obtener la mejor tasa
        result = await service.get_best_exchange_rate(exchange_request)
        
        # Verificar que se devuelve un resultado con error
        assert result.best_provider == "NINGUNO"
        assert result.best_rate == 0.0
        assert result.best_converted_amount == 0.0
        assert result.total_providers_queried == 3
        assert result.successful_providers == 0
        assert result.failed_providers == 3
    
    @pytest.mark.asyncio
    async def test_semaphore_limiting(self, exchange_request):
        """Prueba que el semáforo limita el número de solicitudes concurrentes."""
        # Crear una lista de 10 APIs mock
        apis = [MockAPI(f"API{i}", 0.8 + i/100, 200) for i in range(10)]
        
        # Crear servicio con un límite de 3 solicitudes concurrentes
        service = ExchangeService(apis, max_concurrent_requests=3)
        
        # Espiar el método _get_rate_with_semaphore
        original_method = service._get_rate_with_semaphore
        calls = []
        
        async def spy_method(*args, **kwargs):
            calls.append(1)
            result = await original_method(*args, **kwargs)
            calls.pop()
            return result
        
        service._get_rate_with_semaphore = spy_method
        
        # Obtener la mejor tasa
        result = await service.get_best_exchange_rate(exchange_request)
        
        # Verificar que se seleccionó la mejor tasa
        assert result.best_provider == "API9"
        assert result.best_rate == 0.89
        assert result.best_converted_amount == 890.0
        
        # Verificar que nunca hubo más de 3 llamadas concurrentes
        assert max(calls) <= 3
