"""
滴答清单 SDK 基本使用示例

本示例展示了滴答清单 SDK 的基本功能，包括：
1. 初始化客户端
2. 任务管理（创建、查询、更新、删除）
3. 项目管理（创建、查询、更新、删除）
4. 标签管理（创建、查询、更新、删除）
"""

from dida import DidaClient
from dida.models.task import Task
from dida.models.project import Project
from dida.models.tag import Tag
from datetime import datetime

def main():
    # 初始化客户端
    # 方式1：使用邮箱和密码
    client = DidaClient(email="your_email", password="your_password")
    
    # 方式2：使用token
    # client = DidaClient(token="your_token")
    
    print("\n=== 任务管理示例 ===")
    
    # 创建任务
    new_task = Task(
        title="测试任务",
        content="这是一个测试任务的详细内容",
        priority=3
    )
    created_task = client.tasks.create(new_task)
    print(f"创建任务成功: {created_task.title}")
    
    # 查询所有任务
    tasks = client.tasks.get_all()
    print(f"总任务数: {len(tasks)}")
    
    # 更新任务
    created_task.content = "更新后的任务内容"
    updated_task = client.tasks.update(created_task.id, created_task)
    print(f"更新任务成功: {updated_task.content}")
    
    # 完成任务
    completed_task = client.tasks.complete(updated_task.id)
    print(f"完成任务: {completed_task.is_completed}")
    
    # 删除任务
    client.tasks.delete(completed_task.id, completed_task.project_id)
    print("删除任务成功")
    
    print("\n=== 项目管理示例 ===")
    
    # 创建项目
    new_project = Project(
        name="测试项目",
        color="#FFD324"  # 默认黄色
    )
    created_project = client.projects.create(new_project)
    print(f"创建项目成功: {created_project.name}")
    
    # 获取所有项目
    projects = client.projects.get_all()
    print(f"总项目数: {len(projects)}")
    
    # 更新项目
    created_project.name = "已更新的测试项目"
    success = client.projects.update(created_project.id, created_project)
    print(f"更新项目{'成功' if success else '失败'}")
    
    # 获取项目下的任务
    project_tasks = client.projects.get_tasks(created_project.id)
    print(f"项目任务数: {len(project_tasks)}")
    
    # 删除项目
    success = client.projects.delete(created_project.id)
    print(f"删除项目{'成功' if success else '失败'}")
    
    print("\n=== 标签管理示例 ===")
    
    # 创建标签
    new_tag = Tag(
        name="工作",
        color="#FFD457",  # 使用默认黄色
        sort_order=-1099511693312,  # 默认排序顺序
        sort_type="project"  # 默认排序类型
    )
    created_tag = client.tags.create(new_tag)
    print(f"创建标签成功: {created_tag.name}")
    
    # 创建另一个标签用于合并
    temp_tag = Tag(
        name="临时",
        color="#FF0000",  # 红色
        sort_order=-1099511693312,
        sort_type="project"
    )
    temp_created = client.tags.create(temp_tag)
    print(f"创建临时标签成功: {temp_created.name}")
    
    # 重命名标签
    success = client.tags.rename("临时", "待处理")
    print(f"重命名标签{'成功' if success else '失败'}")
    
    # 获取所有标签
    tags = client.tags.get_all()
    print(f"总标签数: {len(tags)}")
    
    # 合并标签
    success = client.tags.merge("待处理", "工作")
    print(f"合并标签{'成功' if success else '失败'}")
    
    # 获取标签下的任务
    tag_tasks = client.tags.get_tasks("工作")
    print(f"标签任务数: {len(tag_tasks)}")
    
    # 更新标签
    for tag in tags:
        if tag.name == "工作":
            tag.color = "#FF0000"  # 改为红色
            success = client.tags.update(tag.id, tag)
            print(f"更新标签颜色{'成功' if success else '失败'}")
            break
    
    # 删除标签
    for tag in tags:
        if tag.name == "工作":
            success = client.tags.delete(tag.id)
            print(f"删除标签{'成功' if success else '失败'}")
            break

if __name__ == "__main__":
    main() 