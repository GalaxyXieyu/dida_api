"""
滴答清单SDK基础使用示例
"""
from dida import DidaClient
from dida.models import Task, Project, Tag

def main():
    # 创建客户端实例
    client = DidaClient(
        email="your_email@example.com",
        password="your_password"
    )
    
    # 或者使用token
    # client = DidaClient(token="your_token")
    
    # 1. 任务操作示例
    print("\n=== 任务操作示例 ===")
    
    # 创建新任务
    task = Task(
        title="测试任务",
        content="这是一个测试任务",
        priority=3
    )
    new_task = client.tasks.create(task)
    print(f"创建任务成功: {new_task}")
    
    # 获取所有任务
    all_tasks = client.tasks.get_all()
    print(f"总任务数: {len(all_tasks)}")
    
    # 获取已完成的任务
    completed_tasks = client.tasks.get_all({'status': 2})
    print(f"已完成任务数: {len(completed_tasks)}")
    
    # 更新任务
    new_task.title = "更新后的任务"
    updated_task = client.tasks.update(new_task.id, new_task)
    print(f"更新任务成功: {updated_task}")
    
    # 完成任务
    completed_task = client.tasks.complete(new_task.id)
    print(f"完成任务: {completed_task}")
    
    # 删除任务
    if client.tasks.delete(new_task.id, new_task.project_id):
        print("删除任务成功")
    
    # 2. 项目操作示例
    print("\n=== 项目操作示例 ===")
    
    # 创建新项目
    project = Project(
        name="测试项目",
        color="#FF0000"
    )
    new_project = client.projects.create(project)
    print(f"创建项目成功: {new_project}")
    
    # 获取所有项目
    all_projects = client.projects.get_all()
    print(f"总项目数: {len(all_projects)}")
    
    # 更新项目
    new_project.name = "更新后的项目"
    updated_project = client.projects.update(new_project.id, new_project)
    print(f"更新项目成功: {updated_project}")
    
    # 获取项目下的任务
    project_tasks = client.projects.get_tasks(new_project.id)
    print(f"项目任务数: {len(project_tasks)}")
    
    # 删除项目
    if client.projects.delete(new_project.id):
        print("删除项目成功")
    
    # 3. 标签操作示例
    print("\n=== 标签操作示例 ===")
    
    # 创建新标签
    tag = Tag(
        name="重要",
        color="#FF0000"
    )
    new_tag = client.tags.create(tag)
    print(f"创建标签成功: {new_tag}")
    
    # 获取所有标签
    all_tags = client.tags.get_all()
    print(f"总标签数: {len(all_tags)}")
    
    # 更新标签
    new_tag.name = "非常重要"
    updated_tag = client.tags.update(new_tag.id, new_tag)
    print(f"更新标签成功: {updated_tag}")
    
    # 获取标签下的任务
    tag_tasks = client.tags.get_tasks(new_tag.name)
    print(f"标签任务数: {len(tag_tasks)}")
    
    # 删除标签
    if client.tags.delete(new_tag.id):
        print("删除标签成功")

if __name__ == "__main__":
    main() 