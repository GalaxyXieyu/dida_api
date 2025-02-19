"""
任务和笔记相关API
"""
from typing import List, Optional, Dict, Any
from .base import BaseAPI
from ..models.task import Task

class TaskAPI(BaseAPI):
    """任务和笔记相关的API实现"""
    
    def _merge_project_info(self, task_data: Dict[str, Any], projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        合并项目信息到任务数据中
        
        Args:
            task_data: 任务数据
            projects: 项目列表
            
        Returns:
            Dict[str, Any]: 合并后的任务数据
        """
        if not task_data.get('projectId'):
            return task_data
            
        for project in projects:
            if project['id'] == task_data['projectId']:
                task_data['projectName'] = project['name']
                task_data['projectKind'] = project['kind']
                break
                
        return task_data
        
    def _merge_tag_info(self, task_data: Dict[str, Any], tags: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        合并标签信息到任务数据中
        
        Args:
            task_data: 任务数据
            tags: 标签列表
            
        Returns:
            Dict[str, Any]: 合并后的任务数据
        """
        if not task_data.get('tags'):
            return task_data
            
        tag_details = []
        for tag_name in task_data['tags']:
            for tag in tags:
                if tag['name'] == tag_name:
                    tag_details.append({
                        'name': tag['name'],
                        'label': tag['label']
                    })
                    break
        
        task_data['tagDetails'] = tag_details
        return task_data
        
    def _simplify_task_data(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        简化任务数据，只保留必要字段
        
        Args:
            task_data: 原始任务数据
            
        Returns:
            Dict[str, Any]: 简化后的任务数据
        """
        essential_fields = {
            'id': task_data.get('id'),
            'title': task_data.get('title'),
            'content': task_data.get('content'),
            'priority': task_data.get('priority'),
            'status': task_data.get('status'),
            'startDate': task_data.get('startDate'),
            'dueDate': task_data.get('dueDate'),
            'projectName': task_data.get('projectName'),
            'projectKind': task_data.get('projectKind'),
            'tagDetails': task_data.get('tagDetails', []),
            'kind': task_data.get('kind'),
            'isAllDay': task_data.get('isAllDay'),
            'reminder': task_data.get('reminder'),
            'repeatFlag': task_data.get('repeatFlag'),
            'items': task_data.get('items', []),
            'progress': task_data.get('progress', 0)
        }
        
        return {k: v for k, v in essential_fields.items() if v is not None}
    
    def get_all_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        获取所有任务（不包含笔记）
        
        Args:
            filters: 筛选条件
                - status: 任务状态 (0-未完成, 2-已完成)
                - priority: 优先级 (0-5)
                - project_id: 项目ID
                - tag_names: 标签名称列表
                - start_date: 开始时间
                - due_date: 截止时间
                
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        response = self._get("/api/v2/batch/check/0")
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        projects = response.get('projectProfiles', [])
        tags = response.get('tags', [])
        
        # 只处理任务类型
        tasks = [task for task in tasks_data if task.get('kind') == 'TEXT']
        
        # 合并项目和标签信息
        for task in tasks:
            task = self._merge_project_info(task, projects)
            task = self._merge_tag_info(task, tags)
            
        # 简化数据结构
        tasks = [self._simplify_task_data(task) for task in tasks]
        
        # 应用筛选条件
        if filters:
            filtered_tasks = []
            for task in tasks:
                if self._apply_filters(task, filters):
                    filtered_tasks.append(task)
            return filtered_tasks
            
        return tasks
    
    def get_all_notes(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        获取所有笔记
        
        Args:
            filters: 筛选条件
                - project_id: 项目ID
                - tag_names: 标签名称列表
                
        Returns:
            List[Dict[str, Any]]: 笔记列表
        """
        response = self._get("/api/v2/batch/check/0")
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        projects = response.get('projectProfiles', [])
        tags = response.get('tags', [])
        
        # 只处理笔记类型
        notes = [task for task in tasks_data if task.get('kind') == 'NOTE']
        
        # 合并项目和标签信息
        for note in notes:
            note = self._merge_project_info(note, projects)
            note = self._merge_tag_info(note, tags)
            
        # 简化数据结构
        notes = [self._simplify_task_data(note) for note in notes]
        
        # 应用筛选条件
        if filters:
            filtered_notes = []
            for note in notes:
                if self._apply_filters(note, filters):
                    filtered_notes.append(note)
            return filtered_notes
            
        return notes
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            Dict[str, Any]: 创建成功的任务
        """
        task_data['kind'] = 'TEXT'
        response = self._post("/api/v2/task", task_data)
        return self._simplify_task_data(response)
    
    def create_note(self, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新笔记
        
        Args:
            note_data: 笔记数据
            
        Returns:
            Dict[str, Any]: 创建成功的笔记
        """
        note_data['kind'] = 'NOTE'
        response = self._post("/api/v2/task", note_data)
        return self._simplify_task_data(response)
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict[str, Any]: 任务详情
        """
        response = self._get(f"/api/v2/task/{task_id}")
        return self._simplify_task_data(response)
    
    def get_note(self, note_id: str) -> Dict[str, Any]:
        """
        获取笔记详情
        
        Args:
            note_id: 笔记ID
            
        Returns:
            Dict[str, Any]: 笔记详情
        """
        response = self._get(f"/api/v2/task/{note_id}")
        return self._simplify_task_data(response)
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            task_data: 更新的任务数据
            
        Returns:
            Dict[str, Any]: 更新后的任务
        """
        task_data['kind'] = 'TEXT'
        response = self._put(f"/api/v2/task/{task_id}", task_data)
        return self._simplify_task_data(response)
    
    def update_note(self, note_id: str, note_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新笔记
        
        Args:
            note_id: 笔记ID
            note_data: 更新的笔记数据
            
        Returns:
            Dict[str, Any]: 更新后的笔记
        """
        note_data['kind'] = 'NOTE'
        response = self._put(f"/api/v2/task/{note_id}", note_data)
        return self._simplify_task_data(response)
    
    def delete(self, item_id: str, project_id: str) -> bool:
        """
        删除任务或笔记
        
        Args:
            item_id: 任务或笔记ID
            project_id: 项目ID
            
        Returns:
            bool: 是否删除成功
        """
        data = {
            "delete": [
                {
                    "taskId": item_id,
                    "projectId": project_id
                }
            ]
        }
        response = self._post("/api/v2/batch/task", data)
        return True if response else False
    
    def _apply_filters(self, item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        应用筛选条件
        
        Args:
            item: 任务或笔记数据
            filters: 筛选条件
            
        Returns:
            bool: 是否匹配筛选条件
        """
        for key, value in filters.items():
            if key == 'status' and item.get('status') != value:
                return False
            elif key == 'priority' and item.get('priority') != value:
                return False
            elif key == 'project_id' and item.get('projectId') != value:
                return False
            elif key == 'tag_names':
                item_tags = {tag['name'] for tag in item.get('tagDetails', [])}
                if not (item_tags & set(value)):  # 如果没有交集
                    return False
            elif key == 'start_date' and item.get('startDate'):
                if item['startDate'] < value:
                    return False
            elif key == 'due_date' and item.get('dueDate'):
                if item['dueDate'] > value:
                    return False
        return True 