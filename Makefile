PYTHON ?= python3

.PHONY: validate test

validate:
	$(PYTHON) scripts/03_validar_resultados_artigo.py

test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s tests -v
