#!/usr/bin/env python3
"""
Script para pruebas con APIs reales.
Requiere registrarse en servicios como ExchangeRate-API, Fixer.io u Open Exchange Rates
para obtener claves API.
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

from src.models.exchange_models import ExchangeRequest
from src.apis.api1_json_provider import API1JsonProvider
from src.apis.api2_xml_provider import API2XmlProvider
from src.apis.api3_complex_json_provider import API3ComplexJsonProvider
from src.services.exchange_service import ExchangeService


async def run_real_test():
    """Ejecuta pruebas utilizando APIs reales configuradas en el archivo .env."""
    # Cargar variables de entorno
    load_dotenv()
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Verificar si las claves API están configuradas
    api1_key = os.getenv("API1_KEY")
    api1_url = os.getenv("API1_URL")
    api2_key = os.getenv("API2_KEY")
    api2_url = os.getenv("API2_URL")
    api3_key = os.getenv("API3_KEY")
    api3_url = os.getenv("API3_URL")
    
    missing_configs = []
    if not api1_key or not api1_url:
        missing_configs.append("API1")
    if not api2_key or not api2_url:
        missing_configs.append("API2")
    if not api3_key or not api3_url:
        missing_configs.append("API3")
    
    if missing_configs:
        print(f"\n⚠️ ADVERTENCIA: Faltan configuraciones para: {', '.join(missing_configs)}")
        print("Algunas APIs no estarán disponibles para las pruebas.")
        print("Asegúrese de configurar las variables en el archivo .env según el formato en .env.example")
    
    # Crear lista de proveedores disponibles
    providers = []
    
    if api1_key and api1_url:
        providers.append(API1JsonProvider(api_key=api1_key, base_url=api1_url))
        logger.info(f"API1 configurada con URL: {api1_url}")
    
    if api2_key and api2_url:
        providers.append(API2XmlProvider(api_key=api2_key, base_url=api2_url))
        logger.info(f"API2 configurada con URL: {api2_url}")
    
    if api3_key and api3_url:
        providers.append(API3ComplexJsonProvider(api_key=api3_key, base_url=api3_url))
        logger.info(f"API3 configurada con URL: {api3_url}")
    
    if not providers:
        print("\n❌ ERROR: No hay APIs configuradas. Por favor configure al menos una API en el archivo .env")
        return
    
    # Crear servicio de cambio
    service = ExchangeService(providers)
    
    print("\n===== PRUEBA CON APIs REALES =====")
    print(f"Proveedores configurados: {len(providers)}")
    
    # Definir pares de monedas comunes para probar
    test_cases = [
        {"source": "USD", "target": "EUR", "amount": 1000},
        {"source": "EUR", "target": "USD", "amount": 1000},
        {"source": "USD", "target": "GBP", "amount": 500},
        {"source": "GBP", "target": "USD", "amount": 500}
    ]
    
    # Ejecutar pruebas para cada caso
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Caso de prueba {i}: {case['amount']} {case['source']} a {case['target']} ---")
        
        try:
            request = ExchangeRequest(
                source_currency=case["source"],
                target_currency=case["target"],
                amount=case["amount"]
            )
            
            result = await service.get_best_exchange_rate(request)
            
            if result.successful_providers > 0:
                print(f"✅ Mejor proveedor: {result.best_provider}")
                print(f"Mejor tasa: {result.best_rate:.6f}")
                print(f"Cantidad convertida: {result.best_converted_amount:.2f} {case['target']}")
                print(f"Proveedores exitosos: {result.successful_providers}/{result.total_providers_queried}")
                print(f"Tiempo total: {result.total_time_ms:.2f} ms")
            else:
                print(f"❌ No se obtuvo ninguna respuesta exitosa para {case['source']} a {case['target']}")
                
        except Exception as e:
            logger.error(f"Error en caso de prueba {i}: {str(e)}")
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_real_test())
