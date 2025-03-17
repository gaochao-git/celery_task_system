import os
import sys
from celery_app.tasks import long_running_task

if __name__ == "__main__":
    # 添加当前目录到 Python 路径
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # 提交一个测试任务
    result = long_running_task.delay('test_task', {'value': 10})
    print(f"任务已提交，任务ID: {result.id}")
    print("您可以使用以下命令查看任务状态：")
    print(f"python task_manager.py details {result.id} --show-result") 