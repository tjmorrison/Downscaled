# backend/app/tasks/celery_app.py
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery application
celery_app = Celery(
    "snowpack_portal",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.mesowest",
        "app.tasks.aws_forecast", 
        "app.tasks.snowpack",
        "app.tasks.pipeline"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Task routing
    task_routes={
        "app.tasks.mesowest.*": {"queue": "data_fetch"},
        "app.tasks.aws_forecast.*": {"queue": "data_fetch"},
        "app.tasks.snowpack.*": {"queue": "modeling"},
        "app.tasks.pipeline.*": {"queue": "pipeline"}
    },
    
    # Scheduled tasks (Beat schedule)
    beat_schedule={
        # Morning simulation run at 4 AM UTC
        "morning-simulation": {
            "task": "app.tasks.pipeline.run_complete_pipeline",
            "schedule": crontab(hour=settings.MORNING_RUN_HOUR, minute=0),
            "args": ("morning_run",),
        },
        # Evening simulation run at 4 PM UTC  
        "evening-simulation": {
            "task": "app.tasks.pipeline.run_complete_pipeline", 
            "schedule": crontab(hour=settings.EVENING_RUN_HOUR, minute=0),
            "args": ("evening_run",),
        },
        # Daily data cleanup at midnight
        "daily-cleanup": {
            "task": "app.tasks.pipeline.cleanup_old_data",
            "schedule": crontab(hour=0, minute=0),
        },
    },
)

# Task annotations for monitoring
celery_app.conf.task_annotations = {
    "*": {"rate_limit": "100/m"},
    "app.tasks.mesowest.fetch_mesowest_data_task": {
        "rate_limit": "10/m",
        "time_limit": 300,  # 5 minutes
        "soft_time_limit": 240,  # 4 minutes
    },
    "app.tasks.snowpack.run_snowpack_simulation": {
        "rate_limit": "5/m", 
        "time_limit": 1800,  # 30 minutes
        "soft_time_limit": 1500,  # 25 minutes
    },
}