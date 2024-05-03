import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# Create a Limiter instance
redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")
limiter = Limiter(key_func=get_remote_address, storage_uri=redis_url)
