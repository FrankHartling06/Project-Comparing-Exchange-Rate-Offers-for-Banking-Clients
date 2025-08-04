import asyncio
import time
import logging
from typing import List, Dict, Any, Optional

from src.interfaces.exchange_api_interface import ExchangeAPIInterface
from src.models.exchange_models import ExchangeRequest, ExchangeResponse, BestExchangeResult


class ExchangeService:
    """
    Servicio principal que gestiona las consultas a múltiples APIs de cambio
    y selecciona la mejor oferta.
    """
    
    def __init__(self, api_providers: List[ExchangeAPIInterface], max_concurrent_requests: int = 5):
        """
        Inicializa el servicio con una lista de proveedores de API.
        
        Args:
            api_providers: Lista de objetos que implementan ExchangeAPIInterface.
            max_concurrent_requests: Número máximo de solicitudes concurrentes.
        """
        self.api_providers = api_providers
        self.max_concurrent_requests = max_concurrent_requests
        self.logger = logging.getLogger(__name__)
        
    async def get_best_exchange_rate(self, request: ExchangeRequest) -> BestExchangeResult:
        """
        Consulta todas las APIs configuradas y devuelve la mejor oferta.
        
        Args:
            request: Objeto ExchangeRequest con los datos de la solicitud.
            
        Returns:
            BestExchangeResult: Objeto con la mejor oferta encontrada.
        """
        start_time = time.time()
        
        # Crear un semáforo para limitar el número de solicitudes concurrentes
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        # Crear tareas para todas las APIs
        tasks = []
        for provider in self.api_providers:
            tasks.append(self._get_rate_with_semaphore(semaphore, provider, request))
        
        # Ejecutar todas las tareas concurrentemente
        responses = await asyncio.gather(*tasks)
        
        # Calcular tiempo total
        total_time_ms = (time.time() - start_time) * 1000
        
        # Filtrar respuestas exitosas
        successful_responses = [r for r in responses if r.success]
        
        # Contar respuestas exitosas y fallidas
        successful_count = len(successful_responses)
        failed_count = len(responses) - successful_count
        
        # Si no hay respuestas exitosas, devolver un resultado con error
        if not successful_responses:
            self.logger.error("No se obtuvo ninguna respuesta exitosa de las APIs")
            return BestExchangeResult(
                best_provider="NINGUNO",
                best_rate=0.0,
                best_converted_amount=0.0,
                source_currency=request.source_currency,
                target_currency=request.target_currency,
                original_amount=request.amount,
                total_providers_queried=len(self.api_providers),
                successful_providers=0,
                failed_providers=len(self.api_providers),
                total_time_ms=total_time_ms
            )
        
        # Encontrar la mejor oferta (mayor cantidad convertida)
        best_response = max(successful_responses, key=lambda r: r.converted_amount)
        
        # Registrar información sobre la mejor oferta
        self.logger.info(f"Mejor oferta: {best_response.provider_name} con tasa {best_response.rate} "
                         f"y monto convertido {best_response.converted_amount}")
        
        # Crear y devolver el resultado final
        return BestExchangeResult(
            best_provider=best_response.provider_name,
            best_rate=best_response.rate,
            best_converted_amount=best_response.converted_amount,
            source_currency=request.source_currency,
            target_currency=request.target_currency,
            original_amount=request.amount,
            total_providers_queried=len(self.api_providers),
            successful_providers=successful_count,
            failed_providers=failed_count,
            total_time_ms=total_time_ms
        )
    
    async def _get_rate_with_semaphore(self, semaphore: asyncio.Semaphore, 
                                      provider: ExchangeAPIInterface, 
                                      request: ExchangeRequest) -> ExchangeResponse:
        """
        Obtiene la tasa de cambio de un proveedor usando un semáforo para limitar
        el número de solicitudes concurrentes.
        
        Args:
            semaphore: Semáforo para controlar la concurrencia.
            provider: Proveedor de API a consultar.
            request: Objeto ExchangeRequest con los datos de la solicitud.
            
        Returns:
            ExchangeResponse: Respuesta del proveedor.
        """
        async with semaphore:
            try:
                self.logger.debug(f"Consultando proveedor: {provider.name}")
                return await provider.get_exchange_rate(request)
            except Exception as e:
                self.logger.error(f"Error al consultar {provider.name}: {str(e)}")
                return ExchangeResponse(
                    provider_name=provider.name,
                    converted_amount=0.0,
                    rate=0.0,
                    response_time_ms=0.0,
                    success=False,
                    error_message=f"Error inesperado: {str(e)}"
                )
