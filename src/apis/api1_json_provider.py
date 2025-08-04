import time
import asyncio
from typing import Dict, Any, Optional

import aiohttp

from src.interfaces.exchange_api_interface import ExchangeAPIInterface
from src.models.exchange_models import ExchangeRequest, ExchangeResponse


class API1JsonProvider(ExchangeAPIInterface):
    """
    Implementación de la API1 que utiliza formato JSON.
    Input {from, to, value}
    Output {rate}
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = "https://api1.example.com/exchange"):
        super().__init__(api_key, base_url)
        self.name = "API1_JSON"
    
    async def get_exchange_rate(self, request: ExchangeRequest) -> ExchangeResponse:
        """
        Obtiene la tasa de cambio de la API1.
        
        Args:
            request: Objeto ExchangeRequest con los datos de la solicitud.
            
        Returns:
            ExchangeResponse: Objeto con los datos de la respuesta.
        """
        start_time = time.time()
        
        try:
            request_data = self._prepare_request_data(request)
            
            # Configurar headers con API key si está disponible
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=request_data, headers=headers, timeout=10) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status != 200:
                        error_message = f"Error en API1: Código de estado {response.status}"
                        return self._create_error_response(request, error_message, response_time_ms)
                    
                    response_data = await response.json()
                    return self._parse_response(response_data, request, response_time_ms)
                    
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            return self._create_error_response(request, "Timeout al conectar con API1", response_time_ms)
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return self._create_error_response(request, f"Error al procesar la respuesta de API1: {str(e)}", response_time_ms)
    
    def _prepare_request_data(self, request: ExchangeRequest) -> Dict[str, Any]:
        """
        Prepara los datos para la solicitud a la API1.
        
        Args:
            request: Objeto ExchangeRequest con los datos de la solicitud.
            
        Returns:
            Dict[str, Any]: Diccionario con los datos formateados para la API1.
        """
        return {
            "from": request.source_currency,
            "to": request.target_currency,
            "value": request.amount
        }
    
    def _parse_response(self, response_data: Dict[str, Any], request: ExchangeRequest, response_time_ms: float) -> ExchangeResponse:
        """
        Analiza la respuesta de la API1 y la convierte en un objeto ExchangeResponse.
        
        Args:
            response_data: Datos de respuesta de la API1.
            request: Objeto ExchangeRequest original.
            response_time_ms: Tiempo de respuesta en milisegundos.
            
        Returns:
            ExchangeResponse: Objeto con los datos de la respuesta procesada.
        """
        try:
            if "rate" not in response_data:
                return self._create_error_response(request, "Formato de respuesta inválido de API1", response_time_ms)
            
            rate = float(response_data["rate"])
            converted_amount = request.amount * rate
            
            return ExchangeResponse(
                provider_name=self.name,
                converted_amount=converted_amount,
                rate=rate,
                response_time_ms=response_time_ms,
                success=True,
                raw_response=response_data
            )
        except (ValueError, KeyError) as e:
            return self._create_error_response(request, f"Error al procesar datos de API1: {str(e)}", response_time_ms)
