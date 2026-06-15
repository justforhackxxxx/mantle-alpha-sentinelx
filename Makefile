.PHONY: api test web build deploy

api:
	cd apps/api && python3 main.py

test:
	python3 -m unittest discover -s apps/api/tests

web:
	cd apps/web && npm run dev

build:
	cd apps/web && npm run build

deploy:
	./scripts/deploy_signal_registry.sh

