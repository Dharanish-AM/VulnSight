from app.api.router import run_pipeline
# This is a placeholder for Celery workers. 
# The current MVP uses FastAPI BackgroundTasks as a fallback.
print("Celery worker placeholder active. Using BackgroundTasks fallback.")
