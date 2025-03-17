# Broker 设置 - 使用 Redis 作为消息代理
BROKER_URL = 'redis://82.156.146.51:6379/0'

# Backend 设置 - 使用 MySQL 存储任务结果
# 格式: mysql://用户名:密码@主机:端口/数据库名
RESULT_BACKEND = 'db+mysql://gaochao:fffjjj@82.156.146.51:3306/celery_tasks'

# 序列化设置
ACCEPT_CONTENT = ['json']
TASK_SERIALIZER = 'json'
RESULT_SERIALIZER = 'json'
TIMEZONE = 'Asia/Shanghai'
ENABLE_UTC = True

# 定时任务设置
CELERY_BEAT_SCHEDULE = {
    'task-every-30-seconds': {
        'task': 'celery_app.tasks.periodic_task',
        'schedule': 30.0,  # 每30秒执行一次
    },
    'daily-report-task': {
        'task': 'celery_app.tasks.daily_report',
        'schedule': {'hour': 8, 'minute': 0},  # 每天早上8点执行
    },
}

# MySQL 配置
DATABASE_CONFIG = {
    'host': '82.156.146.51',
    'port': 3306,
    'user': 'gaochao',
    'password': 'fffjjj',
    'database': 'celery_tasks',
} 