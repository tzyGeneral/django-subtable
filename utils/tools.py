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



if __name__ == '__main__':
    a = get_now_table_name('ok', '2020_01_02')
    print(a)