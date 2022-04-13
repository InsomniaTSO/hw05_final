from typing import Dict
from django.http import HttpRequest
import datetime


def year(request: HttpRequest) -> Dict[str, int]:
    """Добавляет переменную с текущим годом."""
    now: datetime = datetime.datetime.now()
    return {
        'year': now.year
    }
