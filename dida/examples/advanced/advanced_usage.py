"""
滴答清单 SDK 高级使用示例

本示例展示了滴答清单 SDK 的高级功能，包括：
1. 批量操作
2. 任务过滤和搜索
3. 任务排序
4. 任务移动
5. 标签和项目的组合使用
"""

from dida import DidaClient
from dida.models.task import Task
from dida.models.project import Project
from dida.models.tag import Tag
from datetime import datetime, timedelta

def main():
    # 初始化客户端
    client = DidaClient(email="your_email@example.com", password="your_password")
    
    # 创建测试项目
    project = client.projects.create(Project(name="高级功能测试项目"))
    
    # 创建测试标签
    tag_high = client.tags.create(Tag(name="高优先级", color="#FF0000"))
    tag_medium = client.tags.create(Tag(name="中优先级", color="#FFA500"))
    tag_low = client.tags.create(Tag(name="低优先级", color="#00FF00"))
    
    print("\n=== 批量创建任务示例 ===")
    # 批量创建任务
    tasks = []
    priorities = [4, 3, 2, 1]  # 4最高，1最低
    for i in range(10):
        priority = priorities[i % 4]
        due_date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        
        task = Task(
            title=f"测试任务 {i+1}",
            content=f"这是测试任务 {i+1} 的详细内容",
            priority=priority,
            dueDate=due_date,
            projectId=project.id
        )
        
        # 根据优先级添加标签
        if priority == 4:
            task.tags = [tag_high.id]
        elif priority == 3:
            task.tags = [tag_medium.id]
        else:
            task.tags = [tag_low.id]
            
        tasks.append(task)
    
    # 批量创建任务
    created_tasks = [client.tasks.create(task) for task in tasks]
    print(f"批量创建任务成功，共创建 {len(created_tasks)} 个任务")
    
    print("\n=== 任务过滤和搜索示例 ===")
    # 获取所有任务
    all_tasks = client.tasks.get_all()
    
    # 按优先级过滤
    high_priority_tasks = [task for task in all_tasks if task.priority == 4]
    print(f"高优先级任务数: {len(high_priority_tasks)}")
    
    # 按到期日期过滤（今天到期的任务）
    today = datetime.now().strftime("%Y-%m-%d")
    today_tasks = [task for task in all_tasks if task.dueDate == today]
    print(f"今天到期的任务数: {len(today_tasks)}")
    
    # 按标签过滤
    high_tag_tasks = [task for task in all_tasks if tag_high.id in task.tags]
    print(f"带高优先级标签的任务数: {len(high_tag_tasks)}")
    
    print("\n=== 任务排序示例 ===")
    # 按优先级排序
    sorted_by_priority = sorted(all_tasks, key=lambda x: x.priority, reverse=True)
    print("按优先级排序的前3个任务:")
    for task in sorted_by_priority[:3]:
        print(f"- {task.title} (优先级: {task.priority})")
    
    # 按到期日期排序
    sorted_by_due_date = sorted(all_tasks, key=lambda x: x.dueDate or "9999-12-31")
    print("\n按到期日期排序的前3个任务:")
    for task in sorted_by_due_date[:3]:
        print(f"- {task.title} (到期日期: {task.dueDate})")
    
    print("\n=== 任务移动示例 ===")
    # 创建新项目
    new_project = client.projects.create(Project(name="新项目"))
    
    # 移动第一个任务到新项目
    first_task = created_tasks[0]
    first_task.projectId = new_project.id
    moved_task = client.tasks.update(first_task)
    print(f"已将任务 '{moved_task.title}' 移动到项目 '{new_project.name}'")
    
    print("\n=== 清理示例数据 ===")
    # 删除所有创建的任务
    for task in created_tasks:
        client.tasks.delete(task.id)
    print("删除所有测试任务")
    
    # 删除项目
    client.projects.delete(project.id)
    client.projects.delete(new_project.id)
    print("删除测试项目")
    
    # 删除标签
    client.tags.delete(tag_high.id)
    client.tags.delete(tag_medium.id)
    client.tags.delete(tag_low.id)
    print("删除测试标签")

if __name__ == "__main__":
    main() 