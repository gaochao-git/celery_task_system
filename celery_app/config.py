# Broker 设置 - 使用 Redis 作为消息代理
# 使用新的配置名称 broker_url 替代 BROKER_URL
broker_url = 'redis://82.156.146.51:6379/0'

# Backend 设置 - 使用 MySQL 存储任务结果
# 格式: mysql://用户名:密码@主机:端口/数据库名
result_backend = 'db+mysql://gaochao:fffjjj@82.156.146.51:3306/celery_tasks'

# 序列化设置
accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
timezone = 'Asia/Shanghai'
# 使用新的配置名称 enable_utc 替代 ENABLE_UTC
enable_utc = True

# 添加新的配置项，解决启动时连接重试的警告
broker_connection_retry_on_startup = True

# 定时任务设置
beat_schedule = {
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