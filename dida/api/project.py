"""
项目相关API
"""
from typing import List, Optional, Dict, Any
from .base import BaseAPI
from ..models.project import Project

class ProjectAPI(BaseAPI):
    """项目相关的API实现"""
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Project]:
        """
        获取所有项目
        
        Args:
            filters: 筛选条件
                - name: 项目名称
                - color: 项目颜色
                - group_id: 项目组ID
                - include_tasks: 是否包含任务（默认True）
                
        Returns:
            List[Project]: 项目列表
        """
        response = self._get("/api/v2/batch/check/0")
        projects_data = response.get('projectProfiles', [])
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        
        # 处理项目数据
        result = []
        for project in projects_data:
            match = True
            
            # 应用筛选条件
            if filters:
                # 名称筛选
                if 'name' in filters and project.get('name') != filters['name']:
                    match = False
                    
                # 颜色筛选
                if 'color' in filters and project.get('color') != filters['color']:
                    match = False
                    
                # 项目组筛选
                if 'group_id' in filters and project.get('groupId') != filters['group_id']:
                    match = False
            
            if match:
                project_data = project.copy()
                
                # 添加任务列表（如果需要）
                # 如果filters为None或include_tasks未指定，默认为True
                if not filters or filters.get('include_tasks', True):
                    project_tasks = [
                        task for task in tasks_data
                        if task.get('projectId') == project['id']
                    ]
                    project_data['tasks'] = project_tasks
                    
                result.append(Project.from_dict(project_data))
                
        return result
    
    def create(self, project: Project) -> Project:
        """
        创建新项目
        
        Args:
            project: 项目实例
            
        Returns:
            Project: 创建成功的项目
        """
        response = self._post("/api/v2/project", project.to_dict())
        return Project.from_dict(response)
    
    def get(self, project_id: str) -> Project:
        """
        获取项目详情
        
        Args:
            project_id: 项目ID
            
        Returns:
            Project: 项目实例
        """
        response = self._get(f"/api/v2/project/{project_id}")
        return Project.from_dict(response)
    
    def update(self, project_id: str, project: Project) -> bool:
        """
        更新项目
        
        Args:
            project_id: 项目ID
            project: 更新后的项目实例
            
        Returns:
            bool: 是否更新成功
        """
        response = self._put(f"/api/v2/project/{project_id}", project.to_dict())
        return isinstance(response, bool) and response
    
    def delete(self, project_id: str) -> bool:
        """
        删除项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            bool: 是否删除成功
        """
        return self._delete(f"/api/v2/project/{project_id}")
    
    def get_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """
        获取项目下的所有任务
        
        Args:
            project_id: 项目ID
            
        Returns:
            List[Dict]: 任务列表
        """
        response = self._get("/api/v2/batch/check/0")
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        return [
            task for task in tasks_data
            if task.get('projectId') == project_id
        ] 