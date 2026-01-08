import os
import redis
from dotenv import load_dotenv
from langchain_community.cache import RedisSemanticCache
from langchain_openai import OpenAIEmbeddings
from langchain_core.outputs import Generation
from typing import Optional

# Cargar variables de entorno
load_dotenv('.env', override=True)

class RedisConnector:
    """Class to manage Redis operations and semantic caching."""
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or self._get_redis_url()
        self.redis_client = redis.from_url(self.redis_url)
        self.cache_hits = 0
        self.cache_misses = 0
        self.connector_type = "redis"

    def _get_redis_url(self):
        """Returns the Redis URL based on environment variables."""
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", 6379)
        return f"redis://{redis_host}:{redis_port}"

    def clear_cache(self):
        """Clears all cache entries."""
        self.redis_client.flushall()
        print("Semantic cache cleared")

    def get_cache_keys(self, pattern: str = "llmcache:*"):
        """Get all cache keys matching a pattern."""
        return self.redis_client.keys(pattern)

    def get_cache_size(self) -> int:
        """Returns the number of keys in the cache."""
        return self.redis_client.dbsize()

    def check_history(self):
        """Print the history of the cache keys."""
        all_keys = self.redis_client.keys("llmcache:*")
        for key in all_keys:
            value = self.redis_client.hgetall(key)
            print(f"Key: {key}")
            print(f"Value: {value}")
            print("---")

    def update_cache(self, question: str, answer: str, embeddings: OpenAIEmbeddings, llm_string: str = "default", score_threshold: float = 0.03):
        """Adds a question-answer pair to the cache."""
        semantic_cache = RedisSemanticCache(redis_url=self.redis_url, embedding=embeddings, score_threshold=score_threshold)
        answer = [Generation(text=answer)]  # Ensure answer is a Generation object
        semantic_cache.update(question, return_val=answer, llm_string=llm_string)
        print(f"Added to cache: Q: {question} | A: {answer[0].text}")

    def lookup_cache(self, question: str, embeddings: OpenAIEmbeddings, llm_string: str = "default", score_threshold: float = 0.03) -> Optional[str]:
        """Retrieves an answer from the cache for the given question."""
        semantic_cache = RedisSemanticCache(redis_url=self.redis_url, embedding=embeddings, score_threshold=score_threshold)
        cached_response = semantic_cache.lookup(question, llm_string=llm_string)
        print(f"Checking cache for: '{question}'")

        if cached_response:
            cached_response = cached_response[0].text
            print(f"Cached response: {cached_response}")
            self.cache_hits += 1
            print(f"[CACHE HIT] Retrieved from cache: '{question}'")
        else:
            self.cache_misses += 1
            print(f"[CACHE MISS] Not in cache: '{question}'")
        return cached_response

    def get_cache_stats(self) -> dict:
        """Return cache hit/miss statistics."""
        return {"cache_hits": self.cache_hits, "cache_misses": self.cache_misses}

if __name__ == "__main__":
    redis_connector = RedisConnector()
    redis_connector.check_history()
    redis_connector.clear_cache()
    # redis_connector.check_history()
    print(f"Cache size: {redis_connector.get_cache_size()}")