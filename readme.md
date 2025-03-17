# 创建数据库
mysql> CREATE DATABASE celery_tasks;
# 初始化数据库
python init_db.py
# 启动 Celery Worker
python run_worker.py
# 测试
python test_task.py
# 查看任务状态
python task_manager.py details <task_id> --show-result
