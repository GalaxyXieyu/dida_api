"""
任务数据模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseModel

class Task(BaseModel):
    """任务数据模型"""
    
    def __init__(
        self,
        title: str,
        content: str = "",
        priority: int = 0,
        status: int = 0,
        start_date: Optional[str] = None,
        due_date: Optional[str] = None,
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ):
        """
        初始化任务实例
        
        Args:
            title: 任务标题
            content: 任务内容
            priority: 优先级 (0-最低, 1-低, 3-中, 5-高)
            status: 任务状态 (0-未完成, 2-已完成)
            start_date: 开始时间
            due_date: 截止时间
            project_id: 所属项目ID
            tags: 标签列表
            **kwargs: 其他属性
        """
        self.title = title
        self.content = content
        self.priority = priority
        self.status = status
        self.start_date = self._parse_datetime(start_date)
        self.due_date = self._parse_datetime(due_date)
        self.project_id = project_id
        self.tags = tags or []
        super().__init__(**kwargs)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        从API响应数据创建任务实例
        
        Args:
            data: API响应数据
            
        Returns:
            Task: 任务实例
        """
        return cls(
            title=data.get('title', ''),
            content=data.get('content', ''),
            priority=data.get('priority', 0),
            status=data.get('status', 0),
            start_date=data.get('startDate'),
            due_date=data.get('dueDate'),
            project_id=data.get('projectId'),
            tags=data.get('tags', []),
            id=data.get('id'),
            created=data.get('created'),
            modified=data.get('modified')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将任务转换为API请求数据
        
        Returns:
            Dict: API请求数据
        """
        # 只包含必要的字段
        data = {
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'status': self.status
        }
        
        # 只在有值时添加可选字段
        if self.tags:
            data['tags'] = self.tags
        if self.start_date:
            data['startDate'] = self.start_date.strftime("%Y-%m-%dT%H:%M:%S.000+0000")
        if self.due_date:
            data['dueDate'] = self.due_date.strftime("%Y-%m-%dT%H:%M:%S.000+0000")
        if self.project_id:
            data['projectId'] = self.project_id
        if hasattr(self, 'id') and self.id:
            data['id'] = self.id
        
        return data
    
    @property
    def is_completed(self) -> bool:
        """任务是否已完成"""
        return self.status == 2
    
    @property
    def is_overdue(self) -> bool:
        """任务是否已过期"""
        if not self.due_date:
            return False
        return self.due_date < datetime.now()
    
    def complete(self):
        """将任务标记为已完成"""
        self.status = 2
    
    def uncomplete(self):
        """将任务标记为未完成"""
        self.status = 0
    
    def add_tag(self, tag: str):
        """
        添加标签
        
        Args:
            tag: 标签名称
        """
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str):
        """
        移除标签
        
        Args:
            tag: 标签名称
        """
        if tag in self.tags:
            self.tags.remove(tag) 