from django.db import models, connection
from utils.tools import get_now_table_name
from django.conf import settings


def query_tables_exits(table_name: str):
    """查询一张表是否存在"""
    with connection.cursor() as cursor:
        cursor.execute(f"select count(*)  from information_schema.TABLES t where t.TABLE_SCHEMA ='"
                       f"{settings.DATABASES['default']['NAME']}' and t.TABLE_NAME ='{table_name}'")
        row = cursor.fetchone()

    return row


def create_table(model: 'models.Model'):
    """根据模型生成一张新表"""
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


class NewDynamicModel(object):
    _instance = dict()

    def __new__(cls, base_cls, tb_name):
        """
        创建类根据表名
        :param base_cls: 类名（这个类要models基类）
        :param tb_name: 表名
        """
        new_cls_name = "%s_To_%s" % (base_cls.__name__, '_'.join(map(lambda x: x.capitalize(), tb_name.split('_'))))

        if new_cls_name not in cls._instance:
            new_meta_cls = base_cls.Meta
            new_meta_cls.db_table = tb_name
            model_cls = type(str(new_cls_name), (base_cls,),
                             {'__tablename__': tb_name, 'Meta': new_meta_cls, '__module__': cls.__module__})
            cls._instance[new_cls_name] = model_cls
        return cls._instance[new_cls_name]


class User(models.Model):
    CHOICES = (
        (1, '男'),
        (2, '女'),
        (3, '未知'),
    )
    id = models.AutoField(verbose_name='id', primary_key=True, db_column='id')
    name = models.CharField(max_length=50, default='')
    gender = models.SmallIntegerField(choices=CHOICES, default=1)

    class Meta:
        abstract = True

