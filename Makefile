.PHONY: demo test custom real docker docker-test clean

# Ejecutar la demo con mocks integrados
demo:
	python demo.py

# Ejecutar pruebas personalizadas con mocks
custom:
	python custom_test.py

# Ejecutar pruebas con APIs reales
real:
	python real_test.py

# Ejecutar pruebas unitarias
test:
	python -m pytest --cov=src

# Ejecutar la demo en Docker
docker:
	docker-compose up exchange-app

# Ejecutar pruebas en Docker
docker-test:
	docker-compose up exchange-app-tests

# Limpiar archivos temporales
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -f exchange_app.log
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
