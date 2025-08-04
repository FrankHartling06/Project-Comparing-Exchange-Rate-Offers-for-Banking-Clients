from abc import ABC, abstractmethod
import asyncio
from typing import Dict, Any, Optional

from src.models.exchange_models import ExchangeRequest, ExchangeResponse


class ExchangeAPIInterface(ABC):
    """
    Interfaz abstracta que deben implementar todos los proveedores de API de cambio.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Inicializa la interfaz de API con la clave y URL base opcionales.
        
        Args:
            api_key: Clave de API opcional para autenticación.
            base_url: URL base opcional para las solicitudes.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def get_exchange_rate(self, request: ExchangeRequest) -> ExchangeResponse:
        """
        Método abstracto para obtener la tasa de cambio de una API.
        
        Args:
            request: Objeto ExchangeRequest con los datos de la solicitud.
            
        Returns:
            ExchangeResponse: Objeto con los datos de la respuesta.
        """
        pass
    
    @abstractmethod
    def _prepare_request_data(self, request: ExchangeRequest) -> Dict[str, Any]:
        """
        Prepara los datos para la solicitud a la API.
        
        Args:
            request: Objeto ExchangeRequest con los datos de la solicitud.
            
        Returns:
            Dict[str, Any]: Diccionario con los datos formateados para la API.
        """
        pass
    
    @abstractmethod
    def _parse_response(self, response_data: Dict[str, Any], request: ExchangeRequest) -> ExchangeResponse:
        """
        Analiza la respuesta de la API y la convierte en un objeto ExchangeResponse.
        
        Args:
            response_data: Datos de respuesta de la API.
            request: Objeto ExchangeRequest original.
            
        Returns:
            ExchangeResponse: Objeto con los datos de la respuesta procesada.
        """
        pass
    
    def _create_error_response(self, request: ExchangeRequest, error_message: str, response_time_ms: float = 0) -> ExchangeResponse:
        """
        Crea una respuesta de error.
        
        Args:
            request: Objeto ExchangeRequest original.
            error_message: Mensaje de error.
            response_time_ms: Tiempo de respuesta en milisegundos.
            
        Returns:
            ExchangeResponse: Objeto con los datos de error.
        """
        return ExchangeResponse(
            provider_name=self.name,
            converted_amount=0.0,
            rate=0.0,
            response_time_ms=response_time_ms,
            success=False,
            error_message=error_message
        )
