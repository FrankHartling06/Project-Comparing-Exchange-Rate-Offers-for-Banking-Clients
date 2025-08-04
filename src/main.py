import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
import json

from dotenv import load_dotenv

from src.models.exchange_models import ExchangeRequest, BestExchangeResult
from src.interfaces.exchange_api_interface import ExchangeAPIInterface
from src.apis.api1_json_provider import API1JsonProvider
from src.apis.api2_xml_provider import API2XmlProvider
from src.apis.api3_complex_json_provider import API3ComplexJsonProvider
from src.services.exchange_service import ExchangeService


class ExchangeApplication:
    """
    Aplicación principal para comparar tipos de cambio.
    """
    
    def __init__(self, use_real_apis: bool = False):
        """
        Inicializa la aplicación.
        
        Args:
            use_real_apis: Si es True, utiliza APIs reales; si es False, utiliza URLs de ejemplo.
        """
        # Configurar logging
        self._setup_logging()
        
        # Cargar variables de entorno si se van a usar APIs reales
        if use_real_apis:
            load_dotenv()
        
        # Inicializar proveedores de API
        self.api_providers = self._initialize_api_providers(use_real_apis)
        
        # Inicializar servicio de cambio
        self.exchange_service = ExchangeService(self.api_providers)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Aplicación inicializada correctamente")
    
    def _setup_logging(self):
        """Configura el sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('exchange_app.log')
            ]
        )
    
    def _initialize_api_providers(self, use_real_apis: bool) -> List[ExchangeAPIInterface]:
        """
        Inicializa los proveedores de API.
        
        Args:
            use_real_apis: Si es True, utiliza APIs reales; si es False, utiliza URLs de ejemplo.
            
        Returns:
            List[ExchangeAPIInterface]: Lista de proveedores de API inicializados.
        """
        providers = []
        
        if use_real_apis:
            # Configuración para APIs reales
            api1_key = os.getenv("API1_KEY")
            api1_url = os.getenv("API1_URL")
            providers.append(API1JsonProvider(api_key=api1_key, base_url=api1_url))
            
            api2_key = os.getenv("API2_KEY")
            api2_url = os.getenv("API2_URL")
            providers.append(API2XmlProvider(api_key=api2_key, base_url=api2_url))
            
            api3_key = os.getenv("API3_KEY")
            api3_url = os.getenv("API3_URL")
            providers.append(API3ComplexJsonProvider(api_key=api3_key, base_url=api3_url))
        else:
            # Configuración para APIs de ejemplo
            providers.append(API1JsonProvider())
            providers.append(API2XmlProvider())
            providers.append(API3ComplexJsonProvider())
        
        return providers
    
    async def get_best_exchange_rate(self, source_currency: str, target_currency: str, amount: float) -> BestExchangeResult:
        """
        Obtiene la mejor tasa de cambio para la conversión solicitada.
        
        Args:
            source_currency: Moneda de origen (código de 3 letras).
            target_currency: Moneda de destino (código de 3 letras).
            amount: Cantidad a convertir.
            
        Returns:
            BestExchangeResult: Objeto con la mejor oferta encontrada.
        """
        try:
            # Crear objeto de solicitud
            request = ExchangeRequest(
                source_currency=source_currency,
                target_currency=target_currency,
                amount=amount
            )
            
            # Obtener la mejor oferta
            self.logger.info(f"Solicitando mejor tasa para {amount} {source_currency} a {target_currency}")
            result = await self.exchange_service.get_best_exchange_rate(request)
            
            # Registrar resultado
            self.logger.info(f"Mejor oferta encontrada: {result.best_provider} con tasa {result.best_rate}")
            
            return result
        except Exception as e:
            self.logger.error(f"Error al obtener la mejor tasa: {str(e)}")
            raise
    
    def display_result(self, result: BestExchangeResult):
        """
        Muestra el resultado de la mejor oferta en la consola.
        
        Args:
            result: Objeto BestExchangeResult con la mejor oferta.
        """
        print("\n===== RESULTADO DE LA COMPARACIÓN DE TIPOS DE CAMBIO =====")
        print(f"Conversión: {result.original_amount} {result.source_currency} a {result.target_currency}")
        print(f"Mejor proveedor: {result.best_provider}")
        print(f"Mejor tasa: {result.best_rate:.6f}")
        print(f"Cantidad convertida: {result.best_converted_amount:.2f} {result.target_currency}")
        print(f"Proveedores consultados: {result.total_providers_queried}")
        print(f"Proveedores exitosos: {result.successful_providers}")
        print(f"Proveedores fallidos: {result.failed_providers}")
        print(f"Tiempo total: {result.total_time_ms:.2f} ms")
        print("=======================================================\n")


async def main():
    """Función principal para ejecutar la aplicación desde línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comparador de tipos de cambio')
    parser.add_argument('--source', '-s', required=True, help='Moneda de origen (código de 3 letras)')
    parser.add_argument('--target', '-t', required=True, help='Moneda de destino (código de 3 letras)')
    parser.add_argument('--amount', '-a', type=float, required=True, help='Cantidad a convertir')
    parser.add_argument('--real', '-r', action='store_true', help='Usar APIs reales (requiere archivo .env)')
    
    args = parser.parse_args()
    
    app = ExchangeApplication(use_real_apis=args.real)
    result = await app.get_best_exchange_rate(args.source, args.target, args.amount)
    app.display_result(result)


if __name__ == "__main__":
    asyncio.run(main())
