# django-mysql分表方案

## overview

mysql在数据量较大时，会使用按照时间分表的策略进行优化，自己使用的框架是django，百度了一圈并没有很好的样例来参考，于是乎自己从头写了一个小demo

## 安装

+ 将项目clone到本地
+ pip install -r requirements.txt
+ 配置`settings.py`里的`DATABASES`和`CACHES`，一个是mysql数据库，一个是缓存redis
+ python manage.py runserver

## 大体思路

### 确定表名规则
首先我们要明白的一点是：我们为什么要分表，因为数据量大。于是我们首要的问题就是分表的规则的问题。我这里暂时只讨论使用时间分表的问题。

我们现在要做的是：**无论我给出一个什么时间，我应该计算处理这个时间应该对应什么表**

我们第一个任务便是，建立一个可以根据时间计算表名的方法。
```python
import datetime
import re

def get_now_table_name(table_prefix: str, time_now=None) -> str:
    """
    根据时间获取表名
    :return: table_name
    """
    if not time_now:
        time_now = datetime.datetime.now().date().__format__("%Y_%m_%d")
    else:
        if not re.search('^\d\d\d\d_\d\d_\d\d$', time_now):
            raise ValueError("时间字符串不匹配")
    return f"{table_prefix}_{time_now}"
```

### 确定处理主体
好了我们已经明白了任何一个时间的数据要进那个表了。这个是我们进行分表的基础。接下来我们要明白我们给我们的数据和model一个映射，让model中已经定义到数据模型，和我们分开表里的数据模型一一对应才行。


数据库中的表是和model中的tb_name对应的。也就是说正常情况下django是一个表和一个model对应的。现在想要让一个model对应所有的表是一件困难的事。我想到的方法是让时间段来控制表的对应关系。也就是让代码层来接管class中的tb_name属性。于是我们要用到的就是python中有关源类的知识。

```python
class NewDynamicModel(object):
    _instance = dict()
    def __new__(cls, base_cls, tb_name):
        """
        创建类根据表名
        :param base_cls: 类名(这个类要models基类)
        :param tb_name: 表名
        :return: base_cls类的实例
        """
        new_cls_name = "%s_To_%s" % (base_cls.__name__, '_'.join(map(lambda x: x.capitalize(), tb_name.split('_'))))
        if new_cls_name not in cls._instance:
            new_meta_cls = base_cls.Meta
            new_meta_cls.db_table = tb_name
            model_cls = type(str(new_cls_name), (base_cls,),
                             {'__tablename__': tb_name, 'Meta': new_meta_cls, '__module__': cls.__module__})
            cls._instance[new_cls_name] = model_cls
        return cls._instance[new_cls_name]
```

### 表不存在的问题
上面的方法写好了，但是还是有一个问题。上面方法适用于分表已经完成情况下，表存在后这些新生成的class是可以找到正常的表，但是倘若原来的表不存在的情况下，这些代码就要报错的。更糟糕的是，我们面对的场景下这种像新表中插入数据的任务是经常发生的。

于是我们清楚我们的目标是：**在已经知道model的情况下，使用代码生成表**

```python
from django.db import connection
def create_table(model: 'models.Model'):
    """根据模型生成一张新表"""
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)
```

### 判断表名是否存在
```python
from django.db import connection
def query_tables_exits(table_name: str):
    """查询一张表是否存在"""
    with connection.cursor() as cursor:
        cursor.execute(f"select count(*)  from information_schema.TABLES t where t.TABLE_SCHEMA ='"
                       f"{settings.DATABASES['default']['NAME']}' and t.TABLE_NAME ='{table_name}'")
        row = cursor.fetchone()

    return row
```

剩下的大家随便看看代码就行，写的屎凑合看，目前能用状态