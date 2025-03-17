import os
import sys
import argparse
from datetime import datetime, timedelta
from tabulate import tabulate
from celery_app.models import get_session, Task, PeriodicTaskRun

def list_tasks(args):
    """列出任务"""
    session = get_session()
    
    # 构建查询
    query = session.query(Task)
    
    # 应用过滤条件
    if args.status:
        query = query.filter(Task.status == args.status.upper())
    
    if args.name:
        query = query.filter(Task.name.like(f"%{args.name}%"))
    
    if args.days:
        since_date = datetime.now() - timedelta(days=args.days)
        query = query.filter(Task.created_at >= since_date)
    
    # 排序
    if args.sort == 'created':
        query = query.order_by(Task.created_at.desc())
    elif args.sort == 'completed':
        query = query.order_by(Task.completed_at.desc())
    
    # 限制结果数量
    tasks = query.limit(args.limit).all()
    
    # 格式化输出
    headers = ["ID", "任务ID", "名称", "状态", "创建时间", "完成时间", "重试次数"]
    rows = []
    
    for task in tasks:
        rows.append([
            task.id,
            task.task_id[:8] + "...",  # 截断任务ID以便显示
            task.name,
            task.status,
            task.created_at.strftime("%Y-%m-%d %H:%M:%S") if task.created_at else "-",
            task.completed_at.strftime("%Y-%m-%d %H:%M:%S") if task.completed_at else "-",
            task.retries
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    session.close()

def list_periodic_runs(args):
    """列出定时任务执行记录"""
    session = get_session()
    
    # 构建查询
    query = session.query(PeriodicTaskRun)
    
    # 应用过滤条件
    if args.task_name:
        query = query.filter(PeriodicTaskRun.task_name == args.task_name)
    
    if args.days:
        since_date = datetime.now() - timedelta(days=args.days)
        query = query.filter(PeriodicTaskRun.execution_time >= since_date)
    
    # 排序
    query = query.order_by(PeriodicTaskRun.execution_time.desc())
    
    # 限制结果数量
    runs = query.limit(args.limit).all()
    
    # 格式化输出
    headers = ["ID", "任务名称", "计划时间", "执行时间", "状态"]
    rows = []
    
    for run in runs:
        rows.append([
            run.id,
            run.task_name,
            run.scheduled_time.strftime("%Y-%m-%d %H:%M:%S") if run.scheduled_time else "-",
            run.execution_time.strftime("%Y-%m-%d %H:%M:%S") if run.execution_time else "-",
            run.status
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    session.close()

def show_task_details(args):
    """显示任务详情"""
    session = get_session()
    
    # 查询任务
    task = session.query(Task).filter_by(task_id=args.task_id).first()
    
    if not task:
        print(f"未找到任务ID为 {args.task_id} 的任务")
        session.close()
        return
    
    # 显示详细信息
    print("\n任务详情:")
    print(f"ID: {task.id}")
    print(f"任务ID: {task.task_id}")
    print(f"名称: {task.name}")
    print(f"状态: {task.status}")
    print(f"创建时间: {task.created_at}")
    print(f"开始时间: {task.started_at}")
    print(f"完成时间: {task.completed_at}")
    print(f"重试次数: {task.retries}")
    
    if args.show_args and task.args:
        print(f"\n参数: {task.args}")
    
    if args.show_kwargs and task.kwargs:
        print(f"\n关键字参数: {task.kwargs}")
    
    if args.show_result and task.result:
        print(f"\n结果: {task.result}")
    
    if args.show_traceback and task.traceback:
        print(f"\n错误追踪: {task.traceback}")
    
    session.close()

def main():
    # 添加当前目录到 Python 路径
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    parser = argparse.ArgumentParser(description='Celery 任务管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 列出任务命令
    list_parser = subparsers.add_parser('list', help='列出任务')
    list_parser.add_argument('--status', help='按状态过滤 (PENDING, STARTED, SUCCESS, FAILURE)')
    list_parser.add_argument('--name', help='按任务名称过滤')
    list_parser.add_argument('--days', type=int, default=7, help='显示最近几天的任务')
    list_parser.add_argument('--sort', choices=['created', 'completed'], default='created', help='排序方式')
    list_parser.add_argument('--limit', type=int, default=20, help='显示的最大任务数')
    
    # 列出定时任务执行记录命令
    periodic_parser = subparsers.add_parser('periodic', help='列出定时任务执行记录')
    periodic_parser.add_argument('--task-name', help='按任务名称过滤')
    periodic_parser.add_argument('--days', type=int, default=7, help='显示最近几天的执行记录')
    periodic_parser.add_argument('--limit', type=int, default=20, help='显示的最大记录数')
    
    # 显示任务详情命令
    details_parser = subparsers.add_parser('details', help='显示任务详情')
    details_parser.add_argument('task_id', help='任务ID')
    details_parser.add_argument('--show-args', action='store_true', help='显示任务参数')
    details_parser.add_argument('--show-kwargs', action='store_true', help='显示任务关键字参数')
    details_parser.add_argument('--show-result', action='store_true', help='显示任务结果')
    details_parser.add_argument('--show-traceback', action='store_true', help='显示错误追踪')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_tasks(args)
    elif args.command == 'periodic':
        list_periodic_runs(args)
    elif args.command == 'details':
        show_task_details(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 