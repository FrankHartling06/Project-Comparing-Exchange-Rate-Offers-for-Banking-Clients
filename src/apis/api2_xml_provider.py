import time
import asyncio
from typing import Dict, Any, Optional

import aiohttp
import xmltodict

from src.interfaces.exchange_api_interface import ExchangeAPIInterface
from src.models.exchange_models import ExchangeRequest, ExchangeResponse


class API2XmlProvider(ExchangeAPIInterface):
    """
    Implementación de la API2 que utiliza formato XML.
    Input <XML><From/><To/><Amount/></XML>
    Output <XML><Result/></XML>
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = "https://api2.example.com/exchange"):
        super().__init__(api_key, base_url)
        self.name = "API2_XML"
    
    async def get_exchange_rate(self, request: ExchangeRequest) -> ExchangeResponse:
        """
        Obtiene la tasa de cambio de la API2.
        
        Args:
            request: Objeto ExchangeRequest con los datos de la solicitud.
            
        Returns:
            ExchangeResponse: Objeto con los datos de la respuesta.
        """
        start_time = time.time()
        
        try:
            request_xml = self._prepare_request_data(request)
            
            # Configurar headers con API key si está disponible
            headers = {
                "Content-Type": "application/xml"
            }
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, data=request_xml, headers=headers, timeout=10) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status != 200:
                        error_message = f"Error en API2: Código de estado {response.status}"
                        return self._create_error_response(request, error_message, response_time_ms)
                    
                    response_text = await response.text()
                    try:
                        response_data = xmltodict.parse(response_text)
                        return self._parse_response(response_data, request, response_time_ms)
                    except Exception as e:
                        return self._create_error_response(request, f"Error al parsear XML de API2: {str(e)}", response_time_ms)
                    
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            return self._create_error_response(request, "Timeout al conectar con API2", response_time_ms)
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return self._create_error_response(request, f"Error al procesar la respuesta de API2: {str(e)}", response_time_ms)
    
    def _prepare_request_data(self, request: ExchangeRequest) -> str:
        """
        Prepara los datos para la solicitud a la API2 en formato XML.
        
        Args:
            request: Objeto ExchangeRequest con los datos de la solicitud.
            
        Returns:
            str: Cadena XML con los datos formateados para la API2.
        """
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<XML>
    <From>{request.source_currency}</From>
    <To>{request.target_currency}</To>
    <Amount>{request.amount}</Amount>
</XML>"""
        return xml
    
    def _parse_response(self, response_data: Dict[str, Any], request: ExchangeRequest, response_time_ms: float) -> ExchangeResponse:
        """
        Analiza la respuesta XML de la API2 y la convierte en un objeto ExchangeResponse.
        
        Args:
            response_data: Datos de respuesta de la API2 (ya convertidos de XML a dict).
            request: Objeto ExchangeRequest original.
            response_time_ms: Tiempo de respuesta en milisegundos.
            
        Returns:
            ExchangeResponse: Objeto con los datos de la respuesta procesada.
        """
        try:
            if "XML" not in response_data or "Result" not in response_data["XML"]:
                return self._create_error_response(request, "Formato de respuesta XML inválido de API2", response_time_ms)
            
            result = float(response_data["XML"]["Result"])
            
            # En este caso, asumimos que el resultado es el monto convertido directamente
            converted_amount = result
            # Calculamos la tasa dividiendo el monto convertido entre el monto original
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
            return self._create_error_response(request, f"Error al procesar datos XML de API2: {str(e)}", response_time_ms)
