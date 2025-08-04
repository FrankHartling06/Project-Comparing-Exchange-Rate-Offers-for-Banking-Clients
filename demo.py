#!/usr/bin/env python3
"""
Script de demostración que utiliza mocks predefinidos para simular respuestas de APIs.
"""
import asyncio
import logging
import time
from typing import Dict, Any

from src.models.exchange_models import ExchangeRequest, ExchangeResponse
from src.interfaces.exchange_api_interface import ExchangeAPIInterface
from src.services.exchange_service import ExchangeService


class MockAPI1Provider(ExchangeAPIInterface):
    """Proveedor mock para API1 con respuestas predefinidas."""
    
    def __init__(self):
        super().__init__()
        self.name = "MockAPI1"
    
    async def get_exchange_rate(self, request: ExchangeRequest) -> ExchangeResponse:
        # Simular tiempo de respuesta
        await asyncio.sleep(0.2)
        
        # Simular tasa de cambio
        if request.source_currency == "USD" and request.target_currency == "EUR":
            rate = 0.85
        elif request.source_currency == "EUR" and request.target_currency == "USD":
            rate = 1.18
        else:
            rate = 1.0
        
        converted_amount = request.amount * rate
        
        return ExchangeResponse(
            provider_name=self.name,
            converted_amount=converted_amount,
            rate=rate,
            response_time_ms=200,
            success=True,
            raw_response={"rate": rate}
        )
    
    def _prepare_request_data(self, request: ExchangeRequest) -> Dict[str, Any]:
        return {"from": request.source_currency, "to": request.target_currency, "value": request.amount}
    
    def _parse_response(self, response_data: Dict[str, Any], request: ExchangeRequest) -> ExchangeResponse:
        # No se utiliza en este mock
        pass


class MockAPI2Provider(ExchangeAPIInterface):
    """Proveedor mock para API2 con respuestas predefinidas."""
    
    def __init__(self):
        super().__init__()
        self.name = "MockAPI2"
    
    async def get_exchange_rate(self, request: ExchangeRequest) -> ExchangeResponse:
        # Simular tiempo de respuesta (un poco más lento que API1)
        await asyncio.sleep(0.3)
        
        # Simular tasa de cambio (ligeramente mejor que API1)
        if request.source_currency == "USD" and request.target_currency == "EUR":
            rate = 0.86
        elif request.source_currency == "EUR" and request.target_currency == "USD":
            rate = 1.19
        else:
            rate = 1.0
        
        converted_amount = request.amount * rate
        
        return ExchangeResponse(
            provider_name=self.name,
            converted_amount=converted_amount,
            rate=rate,
            response_time_ms=300,
            success=True,
            raw_response={"XML": {"Result": str(converted_amount)}}
        )
    
    def _prepare_request_data(self, request: ExchangeRequest) -> Dict[str, Any]:
        return {}  # No se utiliza en este mock
    
    def _parse_response(self, response_data: Dict[str, Any], request: ExchangeRequest) -> ExchangeResponse:
        # No se utiliza en este mock
        pass


class MockAPI3Provider(ExchangeAPIInterface):
    """Proveedor mock para API3 con respuestas predefinidas y simulación de error."""
    
    def __init__(self):
        super().__init__()
        self.name = "MockAPI3"
        self.fail = False  # Para simular fallos
    
    async def get_exchange_rate(self, request: ExchangeRequest) -> ExchangeResponse:
        # Simular tiempo de respuesta (más lento que los demás)
        await asyncio.sleep(0.4)
        
        # Simular fallo ocasional
        if self.fail:
            return self._create_error_response(request, "Error simulado en API3", 400)
        
        # Simular tasa de cambio (la mejor de todas)
        if request.source_currency == "USD" and request.target_currency == "EUR":
            rate = 0.87
        elif request.source_currency == "EUR" and request.target_currency == "USD":
            rate = 1.20
        else:
            rate = 1.0
        
        converted_amount = request.amount * rate
        
        return ExchangeResponse(
            provider_name=self.name,
            converted_amount=converted_amount,
            rate=rate,
            response_time_ms=400,
            success=True,
            raw_response={
                "statusCode": 200,
                "message": "Success",
                "data": {"total": converted_amount}
            }
        )
    
    def _prepare_request_data(self, request: ExchangeRequest) -> Dict[str, Any]:
        return {"exchange": {
            "sourceCurrency": request.source_currency,
            "targetCurrency": request.target_currency,
            "quantity": request.amount
        }}
    
    def _parse_response(self, response_data: Dict[str, Any], request: ExchangeRequest) -> ExchangeResponse:
        # No se utiliza en este mock
        pass


async def run_demo():
    """Ejecuta la demostración con diferentes escenarios."""
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Crear instancias de proveedores mock
    api1 = MockAPI1Provider()
    api2 = MockAPI2Provider()
    api3 = MockAPI3Provider()
    
    # Crear servicio de cambio
    service = ExchangeService([api1, api2, api3])
    
    print("\n===== DEMOSTRACIÓN DEL SISTEMA DE COMPARACIÓN DE TIPOS DE CAMBIO =====")
    
    # Escenario 1: Todas las APIs funcionan correctamente
    print("\n--- Escenario 1: Todas las APIs funcionan correctamente ---")
    request = ExchangeRequest(source_currency="USD", target_currency="EUR", amount=1000)
    result = await service.get_best_exchange_rate(request)
    
    print(f"Conversión: {request.amount} {request.source_currency} a {request.target_currency}")
    print(f"Mejor proveedor: {result.best_provider}")
    print(f"Mejor tasa: {result.best_rate:.6f}")
    print(f"Cantidad convertida: {result.best_converted_amount:.2f} {request.target_currency}")
    print(f"Proveedores consultados: {result.total_providers_queried}")
    print(f"Proveedores exitosos: {result.successful_providers}")
    print(f"Proveedores fallidos: {result.failed_providers}")
    print(f"Tiempo total: {result.total_time_ms:.2f} ms")
    
    # Escenario 2: Una API falla
    print("\n--- Escenario 2: Una API falla ---")
    api3.fail = True  # Hacer que API3 falle
    result = await service.get_best_exchange_rate(request)
    
    print(f"Conversión: {request.amount} {request.source_currency} a {request.target_currency}")
    print(f"Mejor proveedor: {result.best_provider}")
    print(f"Mejor tasa: {result.best_rate:.6f}")
    print(f"Cantidad convertida: {result.best_converted_amount:.2f} {request.target_currency}")
    print(f"Proveedores consultados: {result.total_providers_queried}")
    print(f"Proveedores exitosos: {result.successful_providers}")
    print(f"Proveedores fallidos: {result.failed_providers}")
    print(f"Tiempo total: {result.total_time_ms:.2f} ms")
    
    # Escenario 3: Conversión en dirección opuesta
    print("\n--- Escenario 3: Conversión en dirección opuesta ---")
    api3.fail = False  # Restaurar API3
    request = ExchangeRequest(source_currency="EUR", target_currency="USD", amount=1000)
    result = await service.get_best_exchange_rate(request)
    
    print(f"Conversión: {request.amount} {request.source_currency} a {request.target_currency}")
    print(f"Mejor proveedor: {result.best_provider}")
    print(f"Mejor tasa: {result.best_rate:.6f}")
    print(f"Cantidad convertida: {result.best_converted_amount:.2f} {request.target_currency}")
    print(f"Proveedores consultados: {result.total_providers_queried}")
    print(f"Proveedores exitosos: {result.successful_providers}")
    print(f"Proveedores fallidos: {result.failed_providers}")
    print(f"Tiempo total: {result.total_time_ms:.2f} ms")


if __name__ == "__main__":
    asyncio.run(run_demo())
