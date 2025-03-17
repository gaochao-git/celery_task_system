# Celery 任务队列系统

## 项目结构
celery_task_system/
├── celery_app/
│   ├── __init__.py
│   ├── celery.py      # Celery 应用实例
│   ├── config.py      # 配置文件
│   ├── models.py      # 数据库模型
│   ├── scheduler.py   # 自定义调度器
│   └── tasks.py       # 任务定义
├── scripts/
│   ├── init_db.py             # 数据库初始化脚本
│   ├── task_manager.py        # 任务管理工具
│   ├── periodic_task_manager.py # 定时任务管理工具
│   └── test_task.py           # 测试任务提交脚本
├── schema.sql         # 数据库表结构
├── run_worker.py      # Worker 启动脚本
└── requirements.txt   # 项目依赖

## 启动步骤

### 1. 创建数据库和表结构

方法一：直接执行 SQL 脚本（推荐）

## 数据库表结构说明

### celery_task_records 表 - 异步任务记录表
- `id`: 主键ID
- `task_id`: Celery任务ID
- `task_name`: 任务名称
- `task_status`: 任务状态 (PENDING, STARTED, SUCCESS, FAILURE, REVOKED)
- `create_time`: 创建时间
- `update_time`: 更新时间
- `task_start_time`: 开始执行时间
- `task_complete_time`: 完成时间
- `task_result`: 任务结果 (JSON格式)
- `task_traceback`: 错误追踪信息
- `task_retry_count`: 重试次数
- `task_args`: 任务参数 (JSON格式)
- `task_kwargs`: 任务关键字参数 (JSON格式)

### celery_periodic_task_configs 表 - 定时任务配置表
- `id`: 主键ID
- `task_name`: 任务名称
- `task_path`: 任务路径 (例如: celery_app.tasks.periodic_task)
- `task_interval`: 间隔秒数 (用于间隔任务)
- `task_crontab_minute`: Crontab分钟 (0-59, *, */5 等)
- `task_crontab_hour`: Crontab小时 (0-23, *)
- `task_crontab_day_of_week`: Crontab星期 (0-6 或 mon,tue,wed,thu,fri,sat,sun)
- `task_crontab_day_of_month`: Crontab日期 (1-31, *)
- `task_crontab_month_of_year`: Crontab月份 (1-12, *)
- `task_args`: JSON格式的参数
- `task_kwargs`: JSON格式的关键字参数
- `task_enabled`: 是否启用
- `task_last_run_time`: 上次运行时间
- `task_run_count`: 总运行次数
- `create_time`: 创建时间
- `update_time`: 更新时间
- `task_description`: 任务描述

### celery_periodic_task_execution_logs 表 - 定时任务执行记录表
- `id`: 主键ID
- `task_name`: 任务名称
- `task_schedule_time`: 计划执行时间
- `task_execute_time`: 实际执行时间
- `create_time`: 创建时间
- `update_time`: 更新时间
- `task_status`: 执行状态
- `task_result`: 执行结果 (JSON格式)
