import os
import sys
import argparse
import subprocess
from datetime import datetime
import pymysql
from celery_app.config import DATABASE_CONFIG

def backup_database(args):
    """备份数据库"""
    # 创建备份目录（如果不存在）
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(args.output_dir, f"{DATABASE_CONFIG['database']}_{timestamp}.sql")
    
    # 构建 mysqldump 命令
    cmd = [
        'mysqldump',
        f"--host={DATABASE_CONFIG['host']}",
        f"--port={DATABASE_CONFIG['port']}",
        f"--user={DATABASE_CONFIG['user']}",
        f"--password={DATABASE_CONFIG['password']}",
        '--single-transaction',
        '--routines',
        '--triggers',
        '--events',
        DATABASE_CONFIG['database']
    ]
    
    try:
        # 执行备份
        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)
        
        print(f"数据库 {DATABASE_CONFIG['database']} 已备份到 {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"备份失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

def restore_database(args):
    """从备份文件恢复数据库"""
    if not os.path.exists(args.backup_file):
        print(f"备份文件 {args.backup_file} 不存在")
        return
    
    # 构建 mysql 命令
    cmd = [
        'mysql',
        f"--host={DATABASE_CONFIG['host']}",
        f"--port={DATABASE_CONFIG['port']}",
        f"--user={DATABASE_CONFIG['user']}",
        f"--password={DATABASE_CONFIG['password']}",
        DATABASE_CONFIG['database']
    ]
    
    try:
        # 执行恢复
        with open(args.backup_file, 'r') as f:
            subprocess.run(cmd, stdin=f, check=True)
        
        print(f"数据库 {DATABASE_CONFIG['database']} 已从 {args.backup_file} 恢复")
    except subprocess.CalledProcessError as e:
        print(f"恢复失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

def list_backups(args):
    """列出备份文件"""
    if not os.path.exists(args.backup_dir):
        print(f"备份目录 {args.backup_dir} 不存在")
        return
    
    # 获取所有备份文件
    backup_files = [f for f in os.listdir(args.backup_dir) if f.startswith(DATABASE_CONFIG['database']) and f.endswith('.sql')]
    
    if not backup_files:
        print("没有找到备份文件")
        return
    
    # 按修改时间排序
    backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(args.backup_dir, x)), reverse=True)
    
    print("\n可用的备份文件:")
    for i, file in enumerate(backup_files, 1):
        file_path = os.path.join(args.backup_dir, file)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # 转换为MB
        file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{i}. {file} ({file_size:.2f} MB, {file_date})")

def main():
    # 添加当前目录到 Python 路径
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    parser = argparse.ArgumentParser(description='Celery 任务数据库备份工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 备份命令
    backup_parser = subparsers.add_parser('backup', help='备份数据库')
    backup_parser.add_argument('--output-dir', default='./backups', help='备份文件输出目录')
    
    # 恢复命令
    restore_parser = subparsers.add_parser('restore', help='从备份文件恢复数据库')
    restore_parser.add_argument('backup_file', help='备份文件路径')
    
    # 列出备份命令
    list_parser = subparsers.add_parser('list', help='列出备份文件')
    list_parser.add_argument('--backup-dir', default='./backups', help='备份文件目录')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        backup_database(args)
    elif args.command == 'restore':
        restore_database(args)
    elif args.command == 'list':
        list_backups(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 