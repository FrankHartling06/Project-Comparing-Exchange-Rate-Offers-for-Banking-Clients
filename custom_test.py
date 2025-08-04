#!/usr/bin/env python3
"""
Script para pruebas personalizadas con mocks definidos por el usuario.
Permite definir respuestas simuladas personalizadas sin necesidad de APIs externas.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional

from src.models.exchange_models import ExchangeRequest, ExchangeResponse
from src.interfaces.exchange_api_interface import ExchangeAPIInterface
from src.services.exchange_service import ExchangeService


class CustomMockProvider(ExchangeAPIInterface):
    """
    Proveedor mock personalizable para pruebas.
    """
    
    def __init__(self, name: str, response_time_ms: float, rates: Dict[str, Dict[str, float]]):
        """
        Inicializa el proveedor mock personalizado.
        
        Args:
            name: Nombre del proveedor.
            response_time_ms: Tiempo de respuesta simulado en milisegundos.
            rates: Diccionario de tasas de cambio por pares de monedas.
                  Formato: {"USD": {"EUR": 0.85, "GBP": 0.75}, "EUR": {"USD": 1.18}}
        """
        super().__init__()
        self.name = name
        self.response_time_ms = response_time_ms
        self.rates = rates
        self.should_fail = False
    
    async def get_exchange_rate(self, request: ExchangeRequest) -> ExchangeResponse:
        # Simular tiempo de respuesta
        await asyncio.sleep(self.response_time_ms / 1000)
        
        # Simular fallo si está configurado
        if self.should_fail:
            return self._create_error_response(
                request, 
                f"Error simulado en {self.name}", 
                self.response_time_ms
            )
        
        # Buscar la tasa de cambio para el par de monedas
        try:
            rate = self.rates.get(request.source_currency, {}).get(request.target_currency)
            
            # Si no se encuentra la tasa directa, intentar calcularla a través de USD
            if rate is None:
                # Intentar calcular a través de USD si ambas monedas tienen tasas con USD
                if (request.source_currency != "USD" and 
                    "USD" in self.rates.get(request.source_currency, {}) and 
                    request.target_currency in self.rates.get("USD", {})):
                    
                    source_to_usd = self.rates[request.source_currency]["USD"]
                    usd_to_target = self.rates["USD"][request.target_currency]
                    rate = source_to_usd * usd_to_target
                else:
                    return self._create_error_response(
                        request,
                        f"Par de monedas no soportado por {self.name}: {request.source_currency}/{request.target_currency}",
                        self.response_time_ms
                    )
            
            converted_amount = request.amount * rate
            
            return ExchangeResponse(
                provider_name=self.name,
                converted_amount=converted_amount,
                rate=rate,
                response_time_ms=self.response_time_ms,
                success=True,
                raw_response={"rate": rate, "amount": converted_amount}
            )
            
        except Exception as e:
            return self._create_error_response(
                request,
                f"Error al procesar la solicitud en {self.name}: {str(e)}",
                self.response_time_ms
            )
    
    def _prepare_request_data(self, request: ExchangeRequest) -> Dict[str, Any]:
        # No se utiliza en este mock
        return {}
    
    def _parse_response(self, response_data: Dict[str, Any], request: ExchangeRequest) -> ExchangeResponse:
        # No se utiliza en este mock
        pass


async def run_custom_test():
    """Ejecuta pruebas personalizadas con los mocks definidos por el usuario."""
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print("\n===== PRUEBA PERSONALIZADA DEL SISTEMA DE COMPARACIÓN DE TIPOS DE CAMBIO =====")
    
    # Definir tasas de cambio para los proveedores mock
    provider1_rates = {
        "USD": {"EUR": 0.85, "GBP": 0.75, "JPY": 110.0},
        "EUR": {"USD": 1.18, "GBP": 0.88, "JPY": 129.5},
        "GBP": {"USD": 1.33, "EUR": 1.14, "JPY": 147.0},
        "JPY": {"USD": 0.0091, "EUR": 0.0077, "GBP": 0.0068}
    }
    
    provider2_rates = {
        "USD": {"EUR": 0.86, "GBP": 0.76, "JPY": 109.5},
        "EUR": {"USD": 1.17, "GBP": 0.89, "JPY": 130.0},
        "GBP": {"USD": 1.32, "EUR": 1.13, "JPY": 146.5},
        "JPY": {"USD": 0.0092, "EUR": 0.0078, "GBP": 0.0069}
    }
    
    provider3_rates = {
        "USD": {"EUR": 0.84, "GBP": 0.74, "JPY": 110.5},
        "EUR": {"USD": 1.19, "GBP": 0.87, "JPY": 129.0},
        "GBP": {"USD": 1.34, "EUR": 1.15, "JPY": 147.5},
        "JPY": {"USD": 0.0090, "EUR": 0.0076, "GBP": 0.0067}
    }
    
    # Crear proveedores mock
    provider1 = CustomMockProvider("CustomProvider1", 200, provider1_rates)
    provider2 = CustomMockProvider("CustomProvider2", 300, provider2_rates)
    provider3 = CustomMockProvider("CustomProvider3", 250, provider3_rates)
    
    # Crear servicio de cambio
    service = ExchangeService([provider1, provider2, provider3])
    
    # Definir pares de monedas y cantidades para probar
    test_cases = [
        {"source": "USD", "target": "EUR", "amount": 1000},
        {"source": "EUR", "target": "GBP", "amount": 500},
        {"source": "GBP", "target": "JPY", "amount": 200},
        {"source": "JPY", "target": "USD", "amount": 10000}
    ]
    
    # Ejecutar pruebas para cada caso
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Caso de prueba {i}: {case['amount']} {case['source']} a {case['target']} ---")
        
        request = ExchangeRequest(
            source_currency=case["source"],
            target_currency=case["target"],
            amount=case["amount"]
        )
        
        result = await service.get_best_exchange_rate(request)
        
        print(f"Mejor proveedor: {result.best_provider}")
        print(f"Mejor tasa: {result.best_rate:.6f}")
        print(f"Cantidad convertida: {result.best_converted_amount:.2f} {case['target']}")
        print(f"Proveedores exitosos: {result.successful_providers}/{result.total_providers_queried}")
        print(f"Tiempo total: {result.total_time_ms:.2f} ms")
    
    # Probar escenario con un proveedor fallando
    print("\n--- Caso de prueba con un proveedor fallando ---")
    provider2.should_fail = True
    
    request = ExchangeRequest(source_currency="USD", target_currency="EUR", amount=1000)
    result = await service.get_best_exchange_rate(request)
    
    print(f"Mejor proveedor: {result.best_provider}")
    print(f"Mejor tasa: {result.best_rate:.6f}")
    print(f"Cantidad convertida: {result.best_converted_amount:.2f} EUR")
    print(f"Proveedores exitosos: {result.successful_providers}/{result.total_providers_queried}")
    print(f"Proveedores fallidos: {result.failed_providers}")
    print(f"Tiempo total: {result.total_time_ms:.2f} ms")


if __name__ == "__main__":
    asyncio.run(run_custom_test())
