from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework import status
from app.index.cache.dataCache import DataCache
from app.index.cache.dbHolder import UserHolder
from app.index.models import create_table


def insert_one_user(user_dic: dict):
    """插入一个新数据"""
    user_holder = UserHolder(table_prefix='user')
    cache = DataCache()
    table_exits = cache.getValue(key=user_holder.table_name, dbHolder=user_holder, funcName='table_exits')
    if not table_exits:
        create_table(user_holder.model)
    user_holder.inserUser(user_dic)
    cache.deleteKey(f'{user_holder.table_name}_all')


def query_all_user(date: str):
    """获取所有用户"""
    user_holder = UserHolder(table_prefix='user', time_now=date)  # 获取当前日期下的model（时间可以自由指定）
    key = f'{user_holder.table_name}_all'  # 缓存key
    # 从缓存中读取所有数据
    all_user = DataCache().getValue(key=key, dbHolder=user_holder, funcName='getAllUserItem')
    return all_user


class TestView(APIView):
    """测试视图"""
    def get(self, request, *args, **kwargs):
        """查询数据"""
        res = {"code": status.HTTP_200_OK, "msg": "ok"}

        date = request.GET.get('date', '')
        try:
            all_user = query_all_user(date=date)
            res["data"] = all_user
        except Exception as e:
            res["code"] = status.HTTP_500_INTERNAL_SERVER_ERROR
            res["msg"] = str(e)
        return Response(res)

    def post(self, request, *args, **kwargs):
        """向数据库插入一条数据"""
        res = {"code": status.HTTP_200_OK, "msg": "ok"}

        name = request.data.get("name", "huawei")
        try:
            insert_one_user({"name": name})
        except Exception as e:
            res["code"] = status.HTTP_500_INTERNAL_SERVER_ERROR
            res["msg"] = str(e)
        return Response(res)
