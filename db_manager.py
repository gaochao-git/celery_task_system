import os
import sys
import argparse
from datetime import datetime, timedelta
from tabulate import tabulate
import pymysql
from celery_app.models import get_session, Task, PeriodicTaskRun
from celery_app.config import DATABASE_CONFIG

def connect_db():
    """连接到数据库"""
    return pymysql.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        database=DATABASE_CONFIG['database'],
        charset='utf8mb4'
    )

def show_tables(args):
    """显示数据库中的表"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("\n数据库表:")
        for table in tables:
            print(f"- {table[0]}")
    except pymysql.Error as e:
        print(f"数据库错误: {e}")
    finally:
        cursor.close()
        conn.close()

def show_table_schema(args):
    """显示表结构"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DESCRIBE {args.table}")
        columns = cursor.fetchall()
        
        headers = ["字段", "类型", "Null", "键", "默认值", "额外"]
        rows = []
        
        for column in columns:
            rows.append(column)
        
        print(f"\n表 {args.table} 的结构:")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    except pymysql.Error as e:
        print(f"数据库错误: {e}")
    finally:
        cursor.close()
        conn.close()

def execute_query(args):
    """执行自定义SQL查询"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(args.sql)
        
        if cursor.description:  # 如果有结果集
            results = cursor.fetchall()
            
            if results:
                headers = [column[0] for column in cursor.description]
                print("\n查询结果:")
                print(tabulate(results, headers=headers, tablefmt="grid"))
            else:
                print("查询没有返回结果")
        else:
            conn.commit()
            print(f"查询执行成功，影响了 {cursor.rowcount} 行")
    except pymysql.Error as e:
        print(f"数据库错误: {e}")
    finally:
        cursor.close()
        conn.close()

def clean_old_tasks(args):
    """清理旧任务记录"""
    session = get_session()
    
    try:
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=args.days)
        
        # 删除旧任务
        deleted_count = session.query(Task).filter(Task.created_at < cutoff_date).delete()
        session.commit()
        
        print(f"已删除 {deleted_count} 条创建于 {args.days} 天前的任务记录")
    except Exception as e:
        print(f"清理任务时出错: {e}")
        session.rollback()
    finally:
        session.close()

def clean_old_periodic_runs(args):
    """清理旧的定时任务执行记录"""
    session = get_session()
    
    try:
        # 计算截止日期
        cutoff_date = datetime.now() - timedelta(days=args.days)
        
        # 删除旧记录
        deleted_count = session.query(PeriodicTaskRun).filter(PeriodicTaskRun.execution_time < cutoff_date).delete()
        session.commit()
        
        print(f"已删除 {deleted_count} 条 {args.days} 天前的定时任务执行记录")
    except Exception as e:
        print(f"清理定时任务执行记录时出错: {e}")
        session.rollback()
    finally:
        session.close()

def optimize_tables(args):
    """优化数据库表"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 获取所有表
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        # 优化每个表
        for table in tables:
            print(f"正在优化表 {table}...")
            cursor.execute(f"OPTIMIZE TABLE {table}")
            result = cursor.fetchone()
            print(f"- 结果: {result[3]}")
        
        print("所有表优化完成")
    except pymysql.Error as e:
        print(f"数据库错误: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    # 添加当前目录到 Python 路径
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    parser = argparse.ArgumentParser(description='Celery 任务数据库管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 显示表命令
    show_tables_parser = subparsers.add_parser('show-tables', help='显示数据库中的表')
    
    # 显示表结构命令
    schema_parser = subparsers.add_parser('schema', help='显示表结构')
    schema_parser.add_argument('table', help='表名')
    
    # 执行SQL查询命令
    query_parser = subparsers.add_parser('query', help='执行SQL查询')
    query_parser.add_argument('sql', help='SQL查询语句')
    
    # 清理旧任务命令
    clean_tasks_parser = subparsers.add_parser('clean-tasks', help='清理旧任务记录')
    clean_tasks_parser.add_argument('--days', type=int, default=30, help='删除多少天前的任务')
    
    # 清理旧定时任务执行记录命令
    clean_periodic_parser = subparsers.add_parser('clean-periodic', help='清理旧的定时任务执行记录')
    clean_periodic_parser.add_argument('--days', type=int, default=30, help='删除多少天前的记录')
    
    # 优化表命令
    optimize_parser = subparsers.add_parser('optimize', help='优化数据库表')
    
    args = parser.parse_args()
    
    if args.command == 'show-tables':
        show_tables(args)
    elif args.command == 'schema':
        show_table_schema(args)
    elif args.command == 'query':
        execute_query(args)
    elif args.command == 'clean-tasks':
        clean_old_tasks(args)
    elif args.command == 'clean-periodic':
        clean_old_periodic_runs(args)
    elif args.command == 'optimize':
        optimize_tables(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 