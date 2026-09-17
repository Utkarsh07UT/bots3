.PHONY: mix train demo api dashboard

mix:
	python3 scripts/mix_dataset.py

train:
	python3 scripts/train_models.py

demo:
	python3 scripts/run_demo_detection.py

api:
	PYTHONPATH=backend DEMO_ALERTS_PATH=data/processed/alerts/demo_alerts.json uvicorn app.main:app --reload --port 8000

dashboard:
	cd frontend && npm run dev
