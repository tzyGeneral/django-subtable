from app.index.cache import BaseDbHolder
from app.index.models import User, NewDynamicModel, get_now_table_name, query_tables_exits
from app.index.serializer import UserSerializer


class UserHolder(BaseDbHolder):

    def __init__(self, table_prefix: str, time_now=None):
        self.table_name: str = get_now_table_name(table_prefix, time_now)
        self.model = NewDynamicModel(User, self.table_name)

    def table_exits(self) -> bool:
        """判断一张表是否存在"""
        exits_msg = query_tables_exits(table_name=self.table_name)
        if type(exits_msg) == tuple:
            return bool(exits_msg[0])
        else:
            return False

    def inserUser(self, user_dic: dict):
        """新增一个用户"""
        self.model(**user_dic).save()

    def getAllUserItem(self) -> list:
        """获取所有用户信息"""
        userQs = self.model.objects.all()
        userData = UserSerializer(userQs, many=True).data
        return userData
