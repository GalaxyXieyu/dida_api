"""
滴答清单 SDK 任务统计分析示例

本示例展示了如何使用滴答清单 SDK 进行任务数据统计和分析，包括：
1. 时间维度统计（日/周/月完成的任务）
2. 任务状态分析（逾期、即将到期等）
3. 项目维度统计
4. 标签维度统计
5. 生成统计报告
"""

from dida import DidaClient
from datetime import datetime, timedelta
from collections import defaultdict
import calendar
from typing import List, Dict, Any

class TaskAnalytics:
    """任务数据统计分析类"""
    
    def __init__(self, client: DidaClient):
        """
        初始化任务统计分析器
        
        Args:
            client: DidaClient实例
        """
        self.client = client
        self.tasks = self.client.tasks.get_all()
        self.projects = {p.id: p for p in self.client.projects.get_all()}
        self.tags = {t.id: t for t in self.client.tags.get_all()}
        
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """
        获取已逾期的任务
        
        Returns:
            List[Dict]: 逾期任务列表，每个任务包含基本信息和逾期天数
        """
        today = datetime.now().date()
        overdue_tasks = []
        
        for task in self.tasks:
            if not task.is_completed and task.due_date:
                due_date = task.due_date.date()
                if due_date < today:
                    days_overdue = (today - due_date).days
                    overdue_tasks.append({
                        'task': task,
                        'days_overdue': days_overdue,
                        'project': self.projects.get(task.project_id, None)
                    })
        
        return sorted(overdue_tasks, key=lambda x: x['days_overdue'], reverse=True)
    
    def get_due_soon_tasks(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取即将到期的任务
        
        Args:
            days: 未来几天内到期
            
        Returns:
            List[Dict]: 即将到期的任务列表
        """
        today = datetime.now().date()
        future = today + timedelta(days=days)
        due_soon = []
        
        for task in self.tasks:
            if not task.is_completed and task.due_date:
                due_date = task.due_date.date()
                if today <= due_date <= future:
                    days_until_due = (due_date - today).days
                    due_soon.append({
                        'task': task,
                        'days_until_due': days_until_due,
                        'project': self.projects.get(task.project_id, None)
                    })
        
        return sorted(due_soon, key=lambda x: x['days_until_due'])
    
    def get_completed_tasks_by_period(self, period: str = 'week') -> Dict[str, List[Dict[str, Any]]]:
        """
        按时间周期统计已完成的任务
        
        Args:
            period: 统计周期 ('day', 'week', 'month')
            
        Returns:
            Dict: 按周期分组的已完成任务
        """
        completed_tasks = defaultdict(list)
        
        for task in self.tasks:
            if task.is_completed and task.modified:
                completed_date = task.modified.date()
                
                if period == 'day':
                    key = completed_date.strftime('%Y-%m-%d')
                elif period == 'week':
                    # 获取当前周的周一作为key
                    monday = completed_date - timedelta(days=completed_date.weekday())
                    key = monday.strftime('%Y-%m-%d')
                else:  # month
                    key = completed_date.strftime('%Y-%m')
                    
                completed_tasks[key].append({
                    'task': task,
                    'project': self.projects.get(task.project_id, None)
                })
        
        return dict(completed_tasks)
    
    def get_project_statistics(self) -> List[Dict[str, Any]]:
        """
        获取项目维度的任务统计
        
        Returns:
            List[Dict]: 项目统计信息列表
        """
        project_stats = defaultdict(lambda: {
            'total_tasks': 0,
            'completed_tasks': 0,
            'overdue_tasks': 0,
            'high_priority_tasks': 0
        })
        
        today = datetime.now().date()
        
        for task in self.tasks:
            if not task.project_id:
                continue
                
            stats = project_stats[task.project_id]
            stats['total_tasks'] += 1
            
            if task.is_completed:
                stats['completed_tasks'] += 1
            
            if not task.is_completed and task.due_date and task.due_date.date() < today:
                stats['overdue_tasks'] += 1
                
            if task.priority >= 3:  # 高优先级任务
                stats['high_priority_tasks'] += 1
        
        # 转换为列表并添加项目信息
        result = []
        for project_id, stats in project_stats.items():
            project = self.projects.get(project_id)
            if project:
                result.append({
                    'project': project,
                    'statistics': stats,
                    'completion_rate': (stats['completed_tasks'] / stats['total_tasks'] * 100 
                                      if stats['total_tasks'] > 0 else 0)
                })
        
        return sorted(result, key=lambda x: x['completion_rate'], reverse=True)
    
    def get_tag_statistics(self) -> List[Dict[str, Any]]:
        """
        获取标签维度的任务统计
        
        Returns:
            List[Dict]: 标签统计信息列表
        """
        tag_stats = defaultdict(lambda: {
            'total_tasks': 0,
            'completed_tasks': 0,
            'overdue_tasks': 0,
            'high_priority_tasks': 0
        })
        
        today = datetime.now().date()
        
        for task in self.tasks:
            for tag_id in task.tags:
                stats = tag_stats[tag_id]
                stats['total_tasks'] += 1
                
                if task.is_completed:
                    stats['completed_tasks'] += 1
                
                if not task.is_completed and task.due_date and task.due_date.date() < today:
                    stats['overdue_tasks'] += 1
                    
                if task.priority >= 3:  # 高优先级任务
                    stats['high_priority_tasks'] += 1
        
        # 转换为列表并添加标签信息
        result = []
        for tag_id, stats in tag_stats.items():
            tag = self.tags.get(tag_id)
            if tag:
                result.append({
                    'tag': tag,
                    'statistics': stats,
                    'completion_rate': (stats['completed_tasks'] / stats['total_tasks'] * 100 
                                      if stats['total_tasks'] > 0 else 0)
                })
        
        return sorted(result, key=lambda x: x['completion_rate'], reverse=True)
    
    def generate_weekly_report(self, weeks: int = 1) -> str:
        """
        生成周报
        
        Args:
            weeks: 要统计的周数
            
        Returns:
            str: 格式化的周报文本
        """
        today = datetime.now().date()
        start_date = today - timedelta(days=today.weekday() + 7 * (weeks - 1))
        
        # 获取统计数据
        completed_by_week = self.get_completed_tasks_by_period('week')
        overdue_tasks = self.get_overdue_tasks()
        project_stats = self.get_project_statistics()
        
        # 生成报告
        report = []
        report.append(f"# 任务周报 ({start_date.strftime('%Y-%m-%d')} 至 {today.strftime('%Y-%m-%d')})")
        report.append("\n## 1. 任务完成情况")
        
        # 按周统计完成的任务
        for week_start, tasks in completed_by_week.items():
            week_date = datetime.strptime(week_start, '%Y-%m-%d').date()
            if week_date >= start_date:
                report.append(f"\n### {week_start} 这周完成的任务 ({len(tasks)}个):")
                for task_info in tasks:
                    task = task_info['task']
                    project = task_info['project']
                    project_name = project.name if project else "未分类"
                    report.append(f"- [{project_name}] {task.title}")
        
        # 逾期任务统计
        report.append("\n## 2. 逾期任务情况")
        report.append(f"\n当前共有 {len(overdue_tasks)} 个逾期任务:")
        for task_info in overdue_tasks[:10]:  # 只显示前10个最严重的逾期任务
            task = task_info['task']
            days = task_info['days_overdue']
            project = task_info['project']
            project_name = project.name if project else "未分类"
            report.append(f"- [{project_name}] {task.title} (逾期 {days} 天)")
        
        # 项目完成情况
        report.append("\n## 3. 项目完成情况")
        for proj_stat in project_stats:
            project = proj_stat['project']
            stats = proj_stat['statistics']
            completion_rate = proj_stat['completion_rate']
            report.append(f"\n### {project.name}")
            report.append(f"- 总任务数: {stats['total_tasks']}")
            report.append(f"- 已完成: {stats['completed_tasks']} (完成率: {completion_rate:.1f}%)")
            report.append(f"- 逾期任务: {stats['overdue_tasks']}")
            report.append(f"- 高优先级任务: {stats['high_priority_tasks']}")
        
        return "\n".join(report)
    
    def generate_monthly_report(self, months: int = 1) -> str:
        """
        生成月报
        
        Args:
            months: 要统计的月数
            
        Returns:
            str: 格式化的月报文本
        """
        today = datetime.now().date()
        current_month = today.replace(day=1)
        
        # 获取统计数据
        completed_by_month = self.get_completed_tasks_by_period('month')
        project_stats = self.get_project_statistics()
        tag_stats = self.get_tag_statistics()
        
        # 生成报告
        report = []
        report.append(f"# 任务月报 ({current_month.strftime('%Y-%m')})")
        
        # 本月任务完成情况
        month_key = current_month.strftime('%Y-%m')
        month_tasks = completed_by_month.get(month_key, [])
        report.append(f"\n## 1. 本月完成的任务 ({len(month_tasks)}个)")
        
        # 按项目分组显示完成的任务
        tasks_by_project = defaultdict(list)
        for task_info in month_tasks:
            project = task_info['project']
            project_name = project.name if project else "未分类"
            tasks_by_project[project_name].append(task_info['task'])
        
        for project_name, tasks in tasks_by_project.items():
            report.append(f"\n### {project_name} ({len(tasks)}个):")
            for task in tasks:
                report.append(f"- {task.title}")
        
        # 项目统计
        report.append("\n## 2. 项目统计")
        for proj_stat in project_stats:
            project = proj_stat['project']
            stats = proj_stat['statistics']
            completion_rate = proj_stat['completion_rate']
            report.append(f"\n### {project.name}")
            report.append(f"- 总任务数: {stats['total_tasks']}")
            report.append(f"- 已完成: {stats['completed_tasks']} (完成率: {completion_rate:.1f}%)")
            report.append(f"- 逾期任务: {stats['overdue_tasks']}")
            report.append(f"- 高优先级任务: {stats['high_priority_tasks']}")
        
        # 标签统计
        report.append("\n## 3. 标签统计")
        for tag_stat in tag_stats:
            tag = tag_stat['tag']
            stats = tag_stat['statistics']
            completion_rate = tag_stat['completion_rate']
            report.append(f"\n### {tag.name}")
            report.append(f"- 总任务数: {stats['total_tasks']}")
            report.append(f"- 已完成: {stats['completed_tasks']} (完成率: {completion_rate:.1f}%)")
            report.append(f"- 逾期任务: {stats['overdue_tasks']}")
            report.append(f"- 高优先级任务: {stats['high_priority_tasks']}")
        
        return "\n".join(report)

def main():
    # 初始化客户端
    client = DidaClient(email="your_email@example.com", password="your_password")
    
    # 创建任务分析器
    analytics = TaskAnalytics(client)
    
    # 1. 查看逾期任务
    print("\n=== 逾期任务 ===")
    overdue_tasks = analytics.get_overdue_tasks()
    print(f"当前共有 {len(overdue_tasks)} 个逾期任务")
    for task_info in overdue_tasks[:5]:  # 显示前5个最严重的逾期任务
        task = task_info['task']
        days = task_info['days_overdue']
        print(f"- {task.title} (逾期 {days} 天)")
    
    # 2. 查看即将到期的任务
    print("\n=== 即将到期的任务 ===")
    due_soon = analytics.get_due_soon_tasks(days=7)
    print(f"未来7天内有 {len(due_soon)} 个任务到期")
    for task_info in due_soon[:5]:
        task = task_info['task']
        days = task_info['days_until_due']
        print(f"- {task.title} ({days} 天后到期)")
    
    # 3. 查看本周完成的任务
    print("\n=== 本周完成的任务 ===")
    completed_by_week = analytics.get_completed_tasks_by_period('week')
    this_week = datetime.now().date() - timedelta(days=datetime.now().date().weekday())
    this_week_key = this_week.strftime('%Y-%m-%d')
    this_week_tasks = completed_by_week.get(this_week_key, [])
    print(f"本周已完成 {len(this_week_tasks)} 个任务")
    for task_info in this_week_tasks[:5]:
        task = task_info['task']
        print(f"- {task.title}")
    
    # 4. 生成周报
    print("\n=== 生成周报 ===")
    weekly_report = analytics.generate_weekly_report()
    print(weekly_report)
    
    # 5. 生成月报
    print("\n=== 生成月报 ===")
    monthly_report = analytics.generate_monthly_report()
    print(monthly_report)

if __name__ == "__main__":
    main() 