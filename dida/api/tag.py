"""
标签相关API
"""
from typing import List, Optional, Dict, Any
from .base import BaseAPI
from ..models.tag import Tag

class TagAPI(BaseAPI):
    """标签相关的API实现"""
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Tag]:
        """
        获取所有标签
        
        Args:
            filters: 筛选条件
                - names: 标签名称列表
                - color: 标签颜色
                - include_tasks: 是否包含任务（默认True）
                
        Returns:
            List[Tag]: 标签列表
        """
        response = self._get("/api/v2/batch/check/0")
        tags_data = response.get('tags', [])
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        
        # 处理标签数据
        result = []
        for tag in tags_data:
            match = True
            
            # 应用筛选条件
            if filters:
                # 名称筛选
                if 'names' in filters and tag.get('name') not in filters['names']:
                    match = False
                    
                # 颜色筛选
                if 'color' in filters and tag.get('color') != filters['color']:
                    match = False
            
            if match:
                tag_data = tag.copy()
                
                # 添加任务列表（如果需要）
                # 如果filters为None或include_tasks未指定，默认为True
                if not filters or filters.get('include_tasks', True):
                    tag_tasks = [
                        task for task in tasks_data
                        if tag['name'] in task.get('tags', [])
                    ]
                    tag_data['tasks'] = tag_tasks
                    
                result.append(Tag.from_dict(tag_data))
                
        return result
    
    def create(self, tag: Tag) -> Tag:
        """
        创建新标签
        
        Args:
            tag: 标签实例
            
        Returns:
            Tag: 创建成功的标签
        """
        tag_data = {
            "add": [{
                "name": tag.name,
                "label": tag.name,
                "color": tag.color,
                "sortOrder": tag.sort_order,
                "sortType": tag.sort_type,
                "parent": None,
                "type": 1  # 默认为个人标签
            }],
            "update": [],
            "delete": []
        }
        
        response = self._post("/api/v2/batch/tag", tag_data)
        return tag
    
    def rename(self, old_name: str, new_name: str) -> bool:
        """
        重命名标签
        
        Args:
            old_name: 原标签名称
            new_name: 新标签名称
            
        Returns:
            bool: 是否重命名成功
        """
        rename_data = {
            "name": old_name,
            "newName": new_name
        }
        
        response = self._put("/api/v2/tag/rename", rename_data)
        return isinstance(response, bool) and response
    
    def merge(self, source_tag_name: str, target_tag_name: str) -> bool:
        """
        合并标签
        
        Args:
            source_tag_name: 源标签名称（将被合并的标签）
            target_tag_name: 目标标签名称（合并后保留的标签）
            
        Returns:
            bool: 是否合并成功
        """
        merge_data = {
            "fromName": source_tag_name,
            "toName": target_tag_name
        }
        
        response = self._put("/api/v2/tag/merge", merge_data)
        return isinstance(response, bool) and response
    
    def update(self, tag_id: str, tag: Tag) -> bool:
        """
        更新标签
        
        Args:
            tag_id: 标签ID
            tag: 更新后的标签实例
            
        Returns:
            bool: 是否更新成功
        """
        # 获取当前所有标签
        current_tags = self.get_all()
        target_tag = None
        
        # 找到要更新的标签
        for t in current_tags:
            if getattr(t, 'id', None) == tag_id:
                target_tag = t
                break
                
        if not target_tag:
            return False
            
        # 准备更新数据
        update_data = {
            "add": [],
            "update": [{
                "id": tag_id,
                "name": tag.name,
                "label": tag.name,
                "color": tag.color,
                "sortOrder": tag.sort_order,
                "sortType": tag.sort_type,
                "parent": None,
                "type": getattr(target_tag, 'type', 1)
            }],
            "delete": []
        }
        
        response = self._post("/api/v2/batch/tag", update_data)
        return True
    
    def delete(self, tag_id: str) -> bool:
        """
        删除标签
        
        Args:
            tag_id: 标签ID
            
        Returns:
            bool: 是否删除成功
        """
        delete_data = {
            "add": [],
            "update": [],
            "delete": [tag_id]
        }
        
        response = self._post("/api/v2/batch/tag", delete_data)
        return True
    
    def get_tasks(self, tag_name: str) -> List[Dict[str, Any]]:
        """
        获取标签下的所有任务
        
        Args:
            tag_name: 标签名称
            
        Returns:
            List[Dict]: 任务列表
        """
        response = self._get("/api/v2/batch/check/0")
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        return [
            task for task in tasks_data
            if tag_name in task.get('tags', [])
        ] 