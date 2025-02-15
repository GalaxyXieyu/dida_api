"""
任务相关API
"""
from typing import List, Optional, Dict, Any
from .base import BaseAPI
from ..models.task import Task

class TaskAPI(BaseAPI):
    """任务相关的API实现"""
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """
        获取所有任务
        
        Args:
            filters: 筛选条件
                - status: 任务状态 (0-未完成, 2-已完成)
                - priority: 优先级 (0-5)
                - project_id: 项目ID
                - tag_names: 标签名称列表
                - start_date: 开始时间
                - due_date: 截止时间
                
        Returns:
            List[Task]: 任务列表
        """
        response = self._get("/api/v2/batch/check/0")
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        
        # 如果没有筛选条件，直接返回所有任务
        if not filters:
            return [Task.from_dict(task) for task in tasks_data]
            
        # 应用筛选条件
        filtered_tasks = []
        for task in tasks_data:
            match = True
            
            # 状态筛选
            if 'status' in filters and task.get('status') != filters['status']:
                match = False
                
            # 优先级筛选
            if 'priority' in filters and task.get('priority') != filters['priority']:
                match = False
                
            # 项目筛选
            if 'project_id' in filters and task.get('projectId') != filters['project_id']:
                match = False
                
            # 标签筛选
            if 'tag_names' in filters:
                task_tags = set(task.get('tags', []))
                filter_tags = set(filters['tag_names'])
                if not (task_tags & filter_tags):  # 如果没有交集
                    match = False
                    
            # 开始时间筛选
            if 'start_date' in filters and task.get('startDate'):
                if task['startDate'] < filters['start_date']:
                    match = False
                    
            # 截止时间筛选
            if 'due_date' in filters and task.get('dueDate'):
                if task['dueDate'] > filters['due_date']:
                    match = False
            
            if match:
                filtered_tasks.append(Task.from_dict(task))
                
        return filtered_tasks
    
    def create(self, task: Task) -> Task:
        """
        创建新任务
        
        Args:
            task: 任务实例
            
        Returns:
            Task: 创建成功的任务
        """
        response = self._post("/api/v2/task", task.to_dict())
        return Task.from_dict(response)
    
    def get(self, task_id: str) -> Task:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
            
        Returns:
            Task: 任务实例
        """
        response = self._get(f"/api/v2/task/{task_id}")
        return Task.from_dict(response)
    
    def update(self, task_id: str, task: Task) -> Task:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            task: 更新后的任务实例
            
        Returns:
            Task: 更新后的任务
        """
        response = self._put(f"/api/v2/task/{task_id}", task.to_dict())
        return Task.from_dict(response)
    
    def delete(self, task_id: str, project_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            project_id: 项目ID
            
        Returns:
            bool: 是否删除成功
        """
        data = {
            "delete": [
                {
                    "taskId": task_id,
                    "projectId": project_id
                }
            ]
        }
        response = self._post("/api/v2/batch/task", data)
        return True if response else False
    
    def complete(self, task_id: str) -> Task:
        """
        将任务标记为已完成
        
        Args:
            task_id: 任务ID
            
        Returns:
            Task: 更新后的任务
        """
        task = self.get(task_id)
        task.complete()
        return self.update(task_id, task)
    
    def uncomplete(self, task_id: str) -> Task:
        """
        将任务标记为未完成
        
        Args:
            task_id: 任务ID
            
        Returns:
            Task: 更新后的任务
        """
        task = self.get(task_id)
        task.uncomplete()
        return self.update(task_id, task) 