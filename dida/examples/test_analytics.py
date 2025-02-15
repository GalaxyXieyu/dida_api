"""
测试滴答清单SDK的任务分析功能
"""
from dida import DidaClient
from dida.examples.advanced.task_analytics import TaskAnalytics

def main():
    # 初始化客户端
    client = DidaClient(email="your_email", password="your_password")
    
    # 创建任务分析器
    analytics = TaskAnalytics(client)
    
    print("\n=== 1. 查看逾期任务 ===")
    overdue_tasks = analytics.get_overdue_tasks()
    print(f"当前共有 {len(overdue_tasks)} 个逾期任务")
    for task_info in overdue_tasks[:5]:  # 显示前5个最严重的逾期任务
        task = task_info['task']
        days = task_info['days_overdue']
        project = task_info['project']
        project_name = project.name if project else "未分类"
        print(f"- [{project_name}] {task.title} (逾期 {days} 天)")
    
    print("\n=== 2. 查看即将到期的任务 ===")
    due_soon = analytics.get_due_soon_tasks(days=7)
    print(f"未来7天内有 {len(due_soon)} 个任务到期")
    for task_info in due_soon[:5]:
        task = task_info['task']
        days = task_info['days_until_due']
        project = task_info['project']
        project_name = project.name if project else "未分类"
        print(f"- [{project_name}] {task.title} ({days} 天后到期)")
    
    print("\n=== 3. 查看本周完成的任务 ===")
    completed_by_week = analytics.get_completed_tasks_by_period('week')
    for week_start, tasks in completed_by_week.items():
        print(f"\n{week_start} 这周完成的任务 ({len(tasks)}个):")
        for task_info in tasks[:5]:  # 每周只显示前5个任务
            task = task_info['task']
            project = task_info['project']
            project_name = project.name if project else "未分类"
            print(f"- [{project_name}] {task.title}")
    
    print("\n=== 4. 查看本月完成的任务 ===")
    completed_by_month = analytics.get_completed_tasks_by_period('month')
    for month, tasks in completed_by_month.items():
        print(f"\n{month} 月完成的任务 ({len(tasks)}个):")
        for task_info in tasks[:5]:  # 每月只显示前5个任务
            task = task_info['task']
            project = task_info['project']
            project_name = project.name if project else "未分类"
            print(f"- [{project_name}] {task.title}")
    
    print("\n=== 5. 项目统计 ===")
    project_stats = analytics.get_project_statistics()
    for proj_stat in project_stats:
        project = proj_stat['project']
        stats = proj_stat['statistics']
        completion_rate = proj_stat['completion_rate']
        print(f"\n{project.name}:")
        print(f"- 总任务数: {stats['total_tasks']}")
        print(f"- 已完成: {stats['completed_tasks']} (完成率: {completion_rate:.1f}%)")
        print(f"- 逾期任务: {stats['overdue_tasks']}")
        print(f"- 高优先级任务: {stats['high_priority_tasks']}")
    
    print("\n=== 6. 标签统计 ===")
    tag_stats = analytics.get_tag_statistics()
    for tag_stat in tag_stats:
        tag = tag_stat['tag']
        stats = tag_stat['statistics']
        completion_rate = tag_stat['completion_rate']
        print(f"\n{tag.name}:")
        print(f"- 总任务数: {stats['total_tasks']}")
        print(f"- 已完成: {stats['completed_tasks']} (完成率: {completion_rate:.1f}%)")
        print(f"- 逾期任务: {stats['overdue_tasks']}")
        print(f"- 高优先级任务: {stats['high_priority_tasks']}")
    
    print("\n=== 7. 生成周报 ===")
    weekly_report = analytics.generate_weekly_report(weeks=2)  # 生成最近两周的周报
    print(weekly_report)
    
    print("\n=== 8. 生成月报 ===")
    monthly_report = analytics.generate_monthly_report()
    print(monthly_report)

if __name__ == "__main__":
    main() 