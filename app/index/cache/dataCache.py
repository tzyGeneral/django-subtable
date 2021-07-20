from django.core.cache import caches
from app.index.cache import BaseDbHolder
from typing import Any, List


class DataCache():

    def __init__(self, cacheName: str ='default', timeout: int =60 * 60 * 3):
        self.cache = caches[cacheName]
        self.timeout = timeout

    def getValue(self, key: str, dbHolder: 'BaseDbHolder', funcName: str) -> Any:
        """从缓存中读取数据"""
        result = self.cache.get(key)
        if not result:
            result = getattr(dbHolder, funcName)()
            self.cache.set(key, result, self.timeout)
        return result

    def setValue(self, key: str, value: Any) -> None:
        """设置一个缓存"""
        self.cache.set(str(key), value, self.timeout)

    def deleteKey(self, key: str) -> None:
        """删除缓存"""
        self.cache.delete(str(key))

    def deleteKeysList(self, keysList: List[str]) -> None:
        return self.cache.delete_many([str(x) for x in keysList if x])