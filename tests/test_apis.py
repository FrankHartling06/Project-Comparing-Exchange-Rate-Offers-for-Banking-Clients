import pytest
import asyncio
from unittest.mock import patch, MagicMock

from src.models.exchange_models import ExchangeRequest
from src.apis.api1_json_provider import API1JsonProvider
from src.apis.api2_xml_provider import API2XmlProvider
from src.apis.api3_complex_json_provider import API3ComplexJsonProvider


class TestAPI1JsonProvider:
    """Pruebas para el proveedor API1JsonProvider."""
    
    @pytest.fixture
    def api(self):
        """Fixture para crear una instancia de API1JsonProvider."""
        return API1JsonProvider(api_key="test_key", base_url="https://test.api1.com")
    
    @pytest.fixture
    def exchange_request(self):
        """Fixture para crear una solicitud de prueba."""
        return ExchangeRequest(source_currency="USD", target_currency="EUR", amount=1000)
    
    def test_prepare_request_data(self, api, exchange_request):
        """Prueba la preparación de datos para la solicitud."""
        data = api._prepare_request_data(exchange_request)
        assert data == {"from": "USD", "to": "EUR", "value": 1000}
    
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_get_exchange_rate_success(self, mock_post, api, exchange_request):
        """Prueba la obtención de tasa de cambio con éxito."""
        # Configurar el mock para simular una respuesta exitosa
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = MagicMock(return_value={"rate": 0.85})
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Llamar al método bajo prueba
        response = await api.get_exchange_rate(exchange_request)
        
        # Verificar que se llamó a la API con los parámetros correctos
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://test.api1.com"
        assert call_args[1]["json"] == {"from": "USD", "to": "EUR", "value": 1000}
        assert call_args[1]["headers"] == {"Authorization": "Bearer test_key"}
        
        # Verificar la respuesta
        assert response.provider_name == "API1_JSON"
        assert response.converted_amount == 850.0
        assert response.rate == 0.85
        assert response.success is True
        assert response.error_message is None
    
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_get_exchange_rate_http_error(self, mock_post, api, exchange_request):
        """Prueba la obtención de tasa de cambio con error HTTP."""
        # Configurar el mock para simular un error HTTP
        mock_response = MagicMock()
        mock_response.status = 404
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Llamar al método bajo prueba
        response = await api.get_exchange_rate(exchange_request)
        
        # Verificar la respuesta de error
        assert response.provider_name == "API1_JSON"
        assert response.converted_amount == 0.0
        assert response.rate == 0.0
        assert response.success is False
        assert "Código de estado 404" in response.error_message
    
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_get_exchange_rate_invalid_response(self, mock_post, api, exchange_request):
        """Prueba la obtención de tasa de cambio con respuesta inválida."""
        # Configurar el mock para simular una respuesta con formato inválido
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = MagicMock(return_value={"invalid": "response"})
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Llamar al método bajo prueba
        response = await api.get_exchange_rate(exchange_request)
        
        # Verificar la respuesta de error
        assert response.provider_name == "API1_JSON"
        assert response.converted_amount == 0.0
        assert response.rate == 0.0
        assert response.success is False
        assert "Formato de respuesta inválido" in response.error_message
    
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_get_exchange_rate_exception(self, mock_post, api, exchange_request):
        """Prueba la obtención de tasa de cambio con excepción."""
        # Configurar el mock para lanzar una excepción
        mock_post.side_effect = Exception("Error de conexión")
        
        # Llamar al método bajo prueba
        response = await api.get_exchange_rate(exchange_request)
        
        # Verificar la respuesta de error
        assert response.provider_name == "API1_JSON"
        assert response.converted_amount == 0.0
        assert response.rate == 0.0
        assert response.success is False
        assert "Error de conexión" in response.error_message


class TestAPI2XmlProvider:
    """Pruebas para el proveedor API2XmlProvider."""
    
    @pytest.fixture
    def api(self):
        """Fixture para crear una instancia de API2XmlProvider."""
        return API2XmlProvider(api_key="test_key", base_url="https://test.api2.com")
    
    @pytest.fixture
    def exchange_request(self):
        """Fixture para crear una solicitud de prueba."""
        return ExchangeRequest(source_currency="USD", target_currency="EUR", amount=1000)
    
    def test_prepare_request_data(self, api, exchange_request):
        """Prueba la preparación de datos XML para la solicitud."""
        data = api._prepare_request_data(exchange_request)
        assert "<From>USD</From>" in data
        assert "<To>EUR</To>" in data
        assert "<Amount>1000</Amount>" in data
    
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_get_exchange_rate_success(self, mock_post, api, exchange_request):
        """Prueba la obtención de tasa de cambio con éxito."""
        # Configurar el mock para simular una respuesta exitosa
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = MagicMock(return_value="<XML><Result>850</Result></XML>")
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Llamar al método bajo prueba
        response = await api.get_exchange_rate(exchange_request)
        
        # Verificar que se llamó a la API con los parámetros correctos
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://test.api2.com"
        assert "Content-Type" in call_args[1]["headers"]
        assert call_args[1]["headers"]["Content-Type"] == "application/xml"
        assert call_args[1]["headers"]["X-API-Key"] == "test_key"
        
        # Verificar la respuesta
        assert response.provider_name == "API2_XML"
        assert response.converted_amount == 850.0
        assert response.rate == 0.85  # 850 / 1000
        assert response.success is True
        assert response.error_message is None


class TestAPI3ComplexJsonProvider:
    """Pruebas para el proveedor API3ComplexJsonProvider."""
    
    @pytest.fixture
    def api(self):
        """Fixture para crear una instancia de API3ComplexJsonProvider."""
        return API3ComplexJsonProvider(api_key="test_key", base_url="https://test.api3.com")
    
    @pytest.fixture
    def exchange_request(self):
        """Fixture para crear una solicitud de prueba."""
        return ExchangeRequest(source_currency="USD", target_currency="EUR", amount=1000)
    
    def test_prepare_request_data(self, api, exchange_request):
        """Prueba la preparación de datos para la solicitud."""
        data = api._prepare_request_data(exchange_request)
        assert data == {
            "exchange": {
                "sourceCurrency": "USD",
                "targetCurrency": "EUR",
                "quantity": 1000
            }
        }
    
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_get_exchange_rate_success(self, mock_post, api, exchange_request):
        """Prueba la obtención de tasa de cambio con éxito."""
        # Configurar el mock para simular una respuesta exitosa
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = MagicMock(return_value={
            "statusCode": 200,
            "message": "Success",
            "data": {"total": 850}
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Llamar al método bajo prueba
        response = await api.get_exchange_rate(exchange_request)
        
        # Verificar que se llamó a la API con los parámetros correctos
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://test.api3.com"
        assert call_args[1]["json"] == {
            "exchange": {
                "sourceCurrency": "USD",
                "targetCurrency": "EUR",
                "quantity": 1000
            }
        }
        
        # Verificar la respuesta
        assert response.provider_name == "API3_ComplexJSON"
        assert response.converted_amount == 850.0
        assert response.rate == 0.85  # 850 / 1000
        assert response.success is True
        assert response.error_message is None
    
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_get_exchange_rate_api_error(self, mock_post, api, exchange_request):
        """Prueba la obtención de tasa de cambio con error de API."""
        # Configurar el mock para simular un error de API
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = MagicMock(return_value={
            "statusCode": 400,
            "message": "Invalid currency",
            "data": None
        })
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Llamar al método bajo prueba
        response = await api.get_exchange_rate(exchange_request)
        
        # Verificar la respuesta de error
        assert response.provider_name == "API3_ComplexJSON"
        assert response.converted_amount == 0.0
        assert response.rate == 0.0
        assert response.success is False
        assert "Invalid currency" in response.error_message
