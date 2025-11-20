import json
from datetime import datetime, date
from typing import Any

from pydantic import BaseModel


class CacheSerializer:
    @staticmethod
    def serialize(obj: Any) -> str:
        return json.dumps(obj, default=CacheSerializer._custom_serializer)

    @staticmethod
    def deserialize(data: str) -> Any:
        return json.loads(data)

    @staticmethod
    def _custom_serializer(obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, type(None)):
            return None
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")