import hashlib
import json
from typing import Any

from src.core.cache_key_generator import CacheKeyGenerator


class DefaultCacheKeyGenerator(CacheKeyGenerator):
    def __init__(self, namespace: str = "api_cache"):
        self.namespace = namespace

    async def generate_key(self, endpoint: str, params: dict[str, Any]) -> str:
        param_str = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{self.namespace}:{endpoint}:{param_hash}"