import time
import asyncio
from typing import Dict, Any, Optional

import aiohttp

from src.interfaces.exchange_api_interface import ExchangeAPIInterface
from src.models.exchange_models import ExchangeRequest, ExchangeResponse


class API3ComplexJsonProvider(ExchangeAPIInterface):
    """
    Implementación de la API3 que utiliza formato JSON complejo.
    Input {exchange: {sourceCurrency, targetCurrency, quantity}}
    Output {statusCode, message, data: {total}}
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = "https://api3.example.com/exchange"):
        super().__init__(api_key, base_url)
        self.name = "API3_ComplexJSON"
    
    async def get_exchange_rate(self, request: ExchangeRequest) -> ExchangeResponse:
        """
        Obtiene la tasa de cambio de la API3.
        
        Args:
            request: Objeto ExchangeRequest con los datos de la solicitud.
            
        Returns:
            ExchangeResponse: Objeto con los datos de la respuesta.
        """
        start_time = time.time()
        
        try:
            request_data = self._prepare_request_data(request)
            
            # Configurar headers con API key si está disponible
            headers = {
                "Content-Type": "application/json"
            }
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=request_data, headers=headers, timeout=10) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status != 200:
                        error_message = f"Error en API3: Código de estado {response.status}"
                        return self._create_error_response(request, error_message, response_time_ms)
                    
                    response_data = await response.json()
                    return self._parse_response(response_data, request, response_time_ms)
                    
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            return self._create_error_response(request, "Timeout al conectar con API3", response_time_ms)
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return self._create_error_response(request, f"Error al procesar la respuesta de API3: {str(e)}", response_time_ms)
    
    def _prepare_request_data(self, request: ExchangeRequest) -> Dict[str, Any]:
        """
        Prepara los datos para la solicitud a la API3.
        
        Args:
            request: Objeto ExchangeRequest con los datos de la solicitud.
            
        Returns:
            Dict[str, Any]: Diccionario con los datos formateados para la API3.
        """
        return {
            "exchange": {
                "sourceCurrency": request.source_currency,
                "targetCurrency": request.target_currency,
                "quantity": request.amount
            }
        }
    
    def _parse_response(self, response_data: Dict[str, Any], request: ExchangeRequest, response_time_ms: float) -> ExchangeResponse:
        """
        Analiza la respuesta de la API3 y la convierte en un objeto ExchangeResponse.
        
        Args:
            response_data: Datos de respuesta de la API3.
            request: Objeto ExchangeRequest original.
            response_time_ms: Tiempo de respuesta en milisegundos.
            
        Returns:
            ExchangeResponse: Objeto con los datos de la respuesta procesada.
        """
        try:
            # Verificar si la respuesta tiene la estructura esperada
            if "statusCode" not in response_data or "data" not in response_data or "total" not in response_data["data"]:
                return self._create_error_response(request, "Formato de respuesta inválido de API3", response_time_ms)
            
            # Verificar si la operación fue exitosa según el código de estado
            if response_data["statusCode"] != 200:
                error_message = response_data.get("message", "Error desconocido en API3")
                return self._create_error_response(request, error_message, response_time_ms)
            
            # Obtener el monto convertido
            converted_amount = float(response_data["data"]["total"])
            
            # Calcular la tasa dividiendo el monto convertido entre el monto original
            rate = converted_amount / request.amount
            
            return ExchangeResponse(
                provider_name=self.name,
                converted_amount=converted_amount,
                rate=rate,
                response_time_ms=response_time_ms,
                success=True,
                raw_response=response_data
            )
        except (ValueError, KeyError) as e:
            return self._create_error_response(request, f"Error al procesar datos de API3: {str(e)}", response_time_ms)
