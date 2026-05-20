import logging

logger = logging.getLogger(__name__)


def log_task_start(task_name: str, **kwargs) -> None:
    logger.info("Task started: %s | kwargs=%s", task_name, kwargs)


def log_task_complete(task_name: str, **kwargs) -> None:
    logger.info("Task completed: %s | kwargs=%s", task_name, kwargs)
