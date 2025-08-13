from typing import List
from src.auth.redis_database import RedisConnectionManager

class RedisRepository:

    @classmethod
    def add_element_to_set(cls, name: str, value: str):
        cls.add_batch_to_set(name=name, values=[value])
    
    @classmethod
    def add_batch_to_set(cls, name: str, values: List[str]):
        with RedisConnectionManager() as pipeline:
            pipeline.sadd(name, *values)

    @classmethod
    def remove_element_from_set(cls, name: str, value: str):
        with RedisConnectionManager() as pipeline:
            pipeline.srem(name, value)
    
    @classmethod
    def get_all_set_elements(cls, name: str) -> set:
        with RedisConnectionManager() as pipeline:
            members = pipeline.smembers(name)
            members = pipeline.execute()
            return set(members)
    
    @classmethod
    def get_set_element(cls, name: str, value: str) -> str|None:
        with RedisConnectionManager() as pipeline:
            if pipeline.sismember(name, value):
                return value
            else:
                return None
    
    @classmethod
    def clear_set(cls, name: str):
        with RedisConnectionManager() as pipeline:
            pipeline.delete(name)
    
    @classmethod
    def add_item_to_dict(cls, name: str, key: str, value: str):
        cls.add_batch_to_dict(name=name, mapping={key: value})
    
    @classmethod
    def add_batch_to_dict(cls, name: str, mapping: dict):
        with RedisConnectionManager() as pipeline:
            pipeline.hmset(name, mapping)
    
    @classmethod
    def remove_item_from_dict(cls, name: str, key: str):
        with RedisConnectionManager() as pipeline:
            pipeline.hdel(name, key)
    
    @classmethod
    def get_value_from_dict(cls, name: str, key: str) -> str|None:
        with RedisConnectionManager() as pipeline:
            value = pipeline.hget(name, key)
            value = pipeline.execute()
            if value:
                return value[0].decode()
            else:
                return None
    

        
        

redisRep = RedisRepository()