# Sistema de Comparación de Tipos de Cambio para Clientes Bancarios

Este proyecto implementa un sistema que consulta múltiples APIs de tipos de cambio y selecciona la mejor oferta (mayor cantidad convertida) en el menor tiempo posible.

## Características

- Consulta múltiples APIs con diferentes formatos (JSON, XML)
- Procesamiento concurrente de respuestas
- Tolerancia a fallos (funciona incluso si algunas APIs fallan)
- Selección automática de la mejor oferta
- Sin interfaz de usuario (CLI)
- Sin dependencia de bases de datos SQL
- Completamente probado con tests unitarios

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
   ```
   git clone [URL del repositorio]
   cd Project-Comparing-Exchange-Rate-Offers-for-Banking-Clients
   ```

2. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

## Uso

El proyecto ofrece tres formas de probar el sistema:

### 1. Demo con mocks integrados

```
python demo.py
```

Esta opción utiliza respuestas simuladas predefinidas para demostrar la funcionalidad sin necesidad de APIs externas.

### 2. Pruebas personalizadas

```
python custom_test.py
```

Ejecuta pruebas con proveedores mock configurables para diferentes escenarios.

#### Personalización de pruebas

Para personalizar las pruebas en `custom_test.py`:

1. **Modificar tasas de cambio**: Edite los diccionarios `provider1_rates`, `provider2_rates` y `provider3_rates` para establecer las tasas que desee probar.

2. **Añadir nuevos casos**: Modifique la lista `test_cases` para incluir sus propios pares de monedas y cantidades.

3. **Simular fallos**: Configure `provider.should_fail = True` para simular fallos en proveedores específicos.

4. **Ajustar tiempos de respuesta**: Cambie el segundo parámetro al crear los proveedores mock para simular diferentes tiempos de respuesta.

Ejemplo para añadir un caso personalizado:
```python
# Añadir tasas para nuevas monedas
provider1_rates["MXN"] = {"USD": 0.049, "EUR": 0.041}

# Añadir caso de prueba
test_cases.append({"source": "MXN", "target": "EUR", "amount": 5000})
```

### 3. Pruebas con APIs reales

```
python real_test.py
```

Requiere registrarse en servicios como ExchangeRate-API, Fixer.io u Open Exchange Rates para obtener claves API. Configure las claves en un archivo `.env` siguiendo el formato del archivo `.env.example`.

### 4. Pruebas unitarias

```
python -m pytest --cov=src
```

Ejecuta todas las pruebas unitarias y muestra la cobertura del código.

**Nota importante**: Asegúrese de instalar todas las dependencias primero con `pip install -r requirements.txt` antes de ejecutar las pruebas unitarias. El comando requiere que los módulos `pytest` y `pytest-cov` estén instalados.

## Estructura del Proyecto

```
├── src/
│   ├── models/         # Definiciones de datos
│   ├── interfaces/     # Interfaces abstractas
│   ├── apis/           # Implementaciones de APIs
│   ├── services/       # Lógica de negocio
│   └── main.py         # Punto de entrada
├── tests/              # Pruebas unitarias
├── Dockerfile          # Configuración de Docker
├── docker-compose.yml  # Configuración de Docker Compose
├── requirements.txt    # Dependencias
├── pytest.ini         # Configuración de pytest
├── Makefile           # Comandos comunes
├── demo.py            # Script de demostración
├── custom_test.py     # Pruebas personalizadas
├── real_test.py       # Pruebas con APIs reales
└── README.md          # Este archivo
```

## Docker

Para ejecutar el proyecto en un contenedor Docker:

```
docker-compose up
```

O construir y ejecutar manualmente:

```
docker build -t exchange-rate-comparison .
docker run exchange-rate-comparison
```