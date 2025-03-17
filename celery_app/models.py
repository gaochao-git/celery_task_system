from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import pymysql
from celery_app.config import DATABASE_CONFIG

# 注册 PyMySQL 作为 MySQLdb
pymysql.install_as_MySQLdb()

# 创建数据库连接
DB_URL = f"mysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Task(Base):
    """任务模型"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default='PENDING')
    created_at = Column(DateTime, default=datetime.now)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result = Column(Text, nullable=True)
    traceback = Column(Text, nullable=True)
    retries = Column(Integer, default=0)
    args = Column(Text, nullable=True)
    kwargs = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Task {self.task_id} ({self.status})>"

class PeriodicTaskRun(Base):
    """定时任务执行记录"""
    __tablename__ = 'periodic_task_runs'
    
    id = Column(Integer, primary_key=True)
    task_name = Column(String(255), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    execution_time = Column(DateTime, default=datetime.now)
    status = Column(String(50), default='SUCCESS')
    result = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<PeriodicTaskRun {self.task_name} at {self.execution_time}>"

class PeriodicTask(Base):
    """定时任务配置模型"""
    __tablename__ = 'periodic_tasks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    task = Column(String(255), nullable=False)  # 任务路径
    interval = Column(Integer, nullable=True)  # 间隔秒数
    crontab_minute = Column(String(64), nullable=True)
    crontab_hour = Column(String(64), nullable=True)
    crontab_day_of_week = Column(String(64), nullable=True)
    crontab_day_of_month = Column(String(64), nullable=True)
    crontab_month_of_year = Column(String(64), nullable=True)
    args = Column(Text, nullable=True)  # JSON 格式的参数
    kwargs = Column(Text, nullable=True)  # JSON 格式的关键字参数
    enabled = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    total_run_count = Column(Integer, default=0)
    date_changed = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<PeriodicTask {self.name}>"

# 创建数据库表
def init_db():
    Base.metadata.create_all(engine)

# 获取数据库会话
def get_session():
    return Session() 