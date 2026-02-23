import logging
import sys
from pythonjsonlogger.json import JsonFormatter


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "user_id"):
            record.user_id = "-"
        return True


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(user_id)s"
        )
    )
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
