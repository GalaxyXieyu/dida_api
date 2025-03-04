"""
标签相关API
"""
from typing import List, Optional, Dict, Any
from .base import BaseAPI

class TagAPI(BaseAPI):
    """标签相关的API实现"""
    
    def get_tags(self, names: Optional[List[str]] = None, color: Optional[str] = None,
                include_tasks: bool = True) -> List[Dict[str, Any]]:
        """
        获取标签列表，支持多种筛选条件
        
        Args:
            names: 标签名称列表筛选
            color: 标签颜色筛选
            include_tasks: 是否包含任务列表
            
        Returns:
            List[Dict[str, Any]]: 标签列表
        """
        response = self._get("/api/v2/batch/check/0")
        tags_data = response.get('tags', [])
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        
        # 处理标签数据
        result = []
        for tag in tags_data:
            match = True
            
            # 应用筛选条件
            if names and tag.get('name') not in names:
                match = False
            if color and tag.get('color') != color:
                match = False
            
            if match:
                tag_data = tag.copy()
                
                # 添加任务列表（如果需要）
                if include_tasks:
                    tag_tasks = [
                        task for task in tasks_data
                        if tag['name'] in task.get('tags', [])
                    ]
                    tag_data['tasks'] = tag_tasks
                    
                result.append(tag_data)
                
        return result

    def create_tag(self, name: str, color: Optional[str] = None,
                  sort_order: int = 0, sort_type: str = "name",
                  tag_type: int = 1) -> Dict[str, Any]:
        """
        创建新标签
        
        Args:
            name: 标签名称
            color: 标签颜色
            sort_order: 排序顺序
            sort_type: 排序类型
            tag_type: 标签类型（1为个人标签）
            
        Returns:
            Dict[str, Any]: 创建的标签数据
        """
        tag_data = {
            "add": [{
                "name": name,
                "label": name,
                "color": color,
                "sortOrder": sort_order,
                "sortType": sort_type,
                "parent": None,
                "type": tag_type
            }],
            "update": [],
            "delete": []
        }
        
        # 移除None值的字段
        tag_data["add"][0] = {k: v for k, v in tag_data["add"][0].items() if v is not None}
        
        response = self._post("/api/v2/batch/tag", data=tag_data)
        return tag_data["add"][0]

    def get_tag(self, tag_name: str) -> Optional[Dict[str, Any]]:
        """
        获取单个标签的详细信息
        
        Args:
            tag_name: 标签名称
            
        Returns:
            Optional[Dict[str, Any]]: 标签数据，如果标签不存在则返回None
        """
        tags = self.get_tags(names=[tag_name])
        return tags[0] if tags else None

    def update_tag(self, old_name: str, new_name: Optional[str] = None,
                  color: Optional[str] = None, sort_order: Optional[int] = None,
                  sort_type: Optional[str] = None) -> Dict[str, Any]:
        """
        更新标签信息
        
        Args:
            old_name: 原标签名称
            new_name: 新的标签名称
            color: 新的标签颜色
            sort_order: 新的排序顺序
            sort_type: 新的排序类型
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        # 获取当前标签信息
        current_tag = self.get_tag(old_name)
        if not current_tag:
            return {
                "success": False,
                "info": f"未找到名称为 '{old_name}' 的标签",
                "data": None
            }
        
        try:
            # 如果需要重命名标签
            if new_name and new_name != old_name:
                rename_data = {
                    "name": old_name,
                    "newName": new_name
                }
                self._put("/api/v2/tag/rename", data=rename_data)
                old_name = new_name  # 更新后续操作使用的名称
            
            # 构建更新数据
            update_data = {
                "add": [],
                "update": [{
                    "name": new_name or old_name,
                    "label": new_name or old_name,
                    "color": color if color is not None else current_tag.get('color'),
                    "sortOrder": sort_order if sort_order is not None else current_tag.get('sortOrder'),
                    "sortType": sort_type if sort_type is not None else current_tag.get('sortType'),
                    "parent": None,
                    "type": current_tag.get('type', 1)
                }],
                "delete": []
            }
            
            response = self._post("/api/v2/batch/tag", data=update_data)
            return {
                "success": True,
                "info": "标签更新成功",
                "data": update_data["update"][0]
            }
        except Exception as e:
            return {
                "success": False,
                "info": f"更新标签失败: {str(e)}",
                "data": None
            }

    def delete_tag(self, tag_name: str) -> Dict[str, Any]:
        """
        删除标签
        
        Args:
            tag_name: 标签名称
            
        Returns:
            Dict[str, Any]: 删除操作的结果
        """
        try:
            # 获取标签信息用于返回
            tag = self.get_tag(tag_name)
            if not tag:
                return {
                    "success": False,
                    "info": f"未找到名称为 '{tag_name}' 的标签",
                    "data": None
                }
            
            # 准备删除数据
            delete_data = {
                "add": [],
                "update": [],
                "delete": [tag_name]
            }
            
            # 发送删除请求
            self._post("/api/v2/batch/tag", data=delete_data)
            
            return {
                "success": True,
                "info": f"成功删除标签 '{tag_name}'",
                "data": tag
            }
        except Exception as e:
            return {
                "success": False,
                "info": f"删除标签失败: {str(e)}",
                "data": None
            }

    def merge_tags(self, source_tag_name: str, target_tag_name: str) -> Dict[str, Any]:
        """
        合并标签
        
        Args:
            source_tag_name: 源标签名称（将被合并的标签）
            target_tag_name: 目标标签名称（合并后保留的标签）
            
        Returns:
            Dict[str, Any]: 合并操作的结果
        """
        try:
            merge_data = {
                "fromName": source_tag_name,
                "toName": target_tag_name
            }
            
            response = self._put("/api/v2/tag/merge", data=merge_data)
            return {
                "success": True,
                "info": f"成功将标签 '{source_tag_name}' 合并到 '{target_tag_name}'",
                "data": {
                    "source_tag": source_tag_name,
                    "target_tag": target_tag_name
                }
            }
        except Exception as e:
            return {
                "success": False,
                "info": f"合并标签失败: {str(e)}",
                "data": None
            }

    def get_tag_tasks(self, tag_name: str) -> List[Dict[str, Any]]:
        """
        获取标签下的所有任务
        
        Args:
            tag_name: 标签名称
            
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        response = self._get("/api/v2/batch/check/0")
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        return [
            task for task in tasks_data
            if tag_name in task.get('tags', [])
        ] 