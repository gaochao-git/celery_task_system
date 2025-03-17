import os
import sys
from celery_app.models import init_db

if __name__ == '__main__':
    # 添加当前目录到 Python 路径
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # 初始化数据库表
    print("正在初始化数据库表...")
    init_db()
    print("数据库表初始化完成！") 