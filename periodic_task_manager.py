import os
import sys
import json
import argparse
from datetime import datetime
from tabulate import tabulate
from celery_app.models import get_session, PeriodicTask

def list_tasks(args):
    """列出所有定时任务"""
    session = get_session()
    
    try:
        tasks = session.query(PeriodicTask).all()
        
        headers = ["ID", "名称", "任务", "间隔(秒)", "Crontab", "启用", "上次运行", "运行次数"]
        rows = []
        
        for task in tasks:
            crontab_expr = ""
            if task.crontab_minute is not None:
                crontab_expr = f"{task.crontab_minute} {task.crontab_hour} {task.crontab_day_of_month} {task.crontab_month_of_year} {task.crontab_day_of_week}"
            
            rows.append([
                task.id,
                task.name,
                task.task,
                task.interval,
                crontab_expr if crontab_expr else "-",
                "是" if task.enabled else "否",
                task.last_run_at.strftime("%Y-%m-%d %H:%M:%S") if task.last_run_at else "-",
                task.total_run_count
            ])
        
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    finally:
        session.close()

def add_task(args):
    """添加定时任务"""
    session = get_session()
    
    try:
        # 检查任务名称是否已存在
        existing = session.query(PeriodicTask).filter_by(name=args.name).first()
        if existing:
            print(f"错误: 名称为 '{args.name}' 的任务已存在")
            return
        
        # 创建新任务
        new_task = PeriodicTask(
            name=args.name,
            task=args.task,
            description=args.description
        )
        
        # 设置调度类型
        if args.interval:
            new_task.interval = args.interval
        else:
            new_task.crontab_minute = args.minute
            new_task.crontab_hour = args.hour
            new_task.crontab_day_of_week = args.day_of_week
            new_task.crontab_day_of_month = args.day_of_month
            new_task.crontab_month_of_year = args.month_of_year
        
        # 设置参数
        if args.args:
            new_task.args = json.dumps(args.args.split(','))
        
        if args.kwargs:
            kwargs_dict = {}
            for kv in args.kwargs.split(','):
                if ':' in kv:
                    k, v = kv.split(':', 1)
                    kwargs_dict[k.strip()] = v.strip()
            new_task.kwargs = json.dumps(kwargs_dict)
        
        session.add(new_task)
        session.commit()
        
        print(f"成功添加定时任务: {args.name}")
    except Exception as e:
        session.rollback()
        print(f"添加任务时出错: {e}")
    finally:
        session.close()

def update_task(args):
    """更新定时任务"""
    session = get_session()
    
    try:
        task = session.query(PeriodicTask).filter_by(id=args.id).first()
        if not task:
            print(f"错误: ID为 {args.id} 的任务不存在")
            return
        
        # 更新字段
        if args.name:
            task.name = args.name
        
        if args.task:
            task.task = args.task
        
        if args.description:
            task.description = args.description
        
        if args.interval is not None:
            task.interval = args.interval
            # 清除 crontab 设置
            task.crontab_minute = None
            task.crontab_hour = None
            task.crontab_day_of_week = None
            task.crontab_day_of_month = None
            task.crontab_month_of_year = None
        
        if args.minute is not None:
            # 设置为 crontab 模式
            task.interval = None
            task.crontab_minute = args.minute
            task.crontab_hour = args.hour
            task.crontab_day_of_week = args.day_of_week
            task.crontab_day_of_month = args.day_of_month
            task.crontab_month_of_year = args.month_of_year
        
        if args.args:
            task.args = json.dumps(args.args.split(','))
        
        if args.kwargs:
            kwargs_dict = {}
            for kv in args.kwargs.split(','):
                if ':' in kv:
                    k, v = kv.split(':', 1)
                    kwargs_dict[k.strip()] = v.strip()
            task.kwargs = json.dumps(kwargs_dict)
        
        if args.enabled is not None:
            task.enabled = args.enabled
        
        session.commit()
        print(f"成功更新任务 ID: {args.id}")
    except Exception as e:
        session.rollback()
        print(f"更新任务时出错: {e}")
    finally:
        session.close()

def delete_task(args):
    """删除定时任务"""
    session = get_session()
    
    try:
        task = session.query(PeriodicTask).filter_by(id=args.id).first()
        if not task:
            print(f"错误: ID为 {args.id} 的任务不存在")
            return
        
        session.delete(task)
        session.commit()
        print(f"成功删除任务 ID: {args.id}")
    except Exception as e:
        session.rollback()
        print(f"删除任务时出错: {e}")
    finally:
        session.close()

def main():
    # 添加当前目录到 Python 路径
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    parser = argparse.ArgumentParser(description='Celery 定时任务管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 列出任务命令
    list_parser = subparsers.add_parser('list', help='列出所有定时任务')
    
    # 添加任务命令
    add_parser = subparsers.add_parser('add', help='添加定时任务')
    add_parser.add_argument('--name', required=True, help='任务名称')
    add_parser.add_argument('--task', required=True, help='任务路径 (例如: celery_app.tasks.periodic_task)')
    add_parser.add_argument('--interval', type=int, help='间隔秒数 (与 crontab 参数互斥)')
    add_parser.add_argument('--minute', help='Crontab 分钟 (0-59, *, */5 等)')
    add_parser.add_argument('--hour', help='Crontab 小时 (0-23, *)')
    add_parser.add_argument('--day-of-week', help='Crontab 星期 (0-6 或 mon,tue,wed,thu,fri,sat,sun)')
    add_parser.add_argument('--day-of-month', help='Crontab 日期 (1-31, *)')
    add_parser.add_argument('--month-of-year', help='Crontab 月份 (1-12, *)')
    add_parser.add_argument('--args', help='参数，逗号分隔 (例如: arg1,arg2)')
    add_parser.add_argument('--kwargs', help='关键字参数，逗号分隔 (例如: key1:value1,key2:value2)')
    add_parser.add_argument('--description', help='任务描述')
    
    # 更新任务命令
    update_parser = subparsers.add_parser('update', help='更新定时任务')
    update_parser.add_argument('id', type=int, help='任务ID')
    update_parser.add_argument('--name', help='任务名称')
    update_parser.add_argument('--task', help='任务路径')
    update_parser.add_argument('--interval', type=int, help='间隔秒数')
    update_parser.add_argument('--minute', help='Crontab 分钟')
    update_parser.add_argument('--hour', help='Crontab 小时')
    update_parser.add_argument('--day-of-week', help='Crontab 星期')
    update_parser.add_argument('--day-of-month', help='Crontab 日期')
    update_parser.add_argument('--month-of-year', help='Crontab 月份')
    update_parser.add_argument('--args', help='参数，逗号分隔')
    update_parser.add_argument('--kwargs', help='关键字参数，逗号分隔')
    update_parser.add_argument('--enabled', type=bool, help='是否启用')
    update_parser.add_argument('--description', help='任务描述')
    
    # 删除任务命令
    delete_parser = subparsers.add_parser('delete', help='删除定时任务')
    delete_parser.add_argument('id', type=int, help='任务ID')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_tasks(args)
    elif args.command == 'add':
        add_task(args)
    elif args.command == 'update':
        update_task(args)
    elif args.command == 'delete':
        delete_task(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 