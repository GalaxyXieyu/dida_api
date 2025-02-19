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
        sort_order: int = 0,
        time_zone: str = "Asia/Shanghai",
        is_floating: bool = False,
        is_all_day: bool = False,
        reminder: str = "",
        reminders: Optional[List[str]] = None,
        repeat_flag: str = "",
        ex_date: Optional[List[str]] = None,
        items: Optional[List[Dict]] = None,
        progress: int = 0,
        modified_time: Optional[str] = None,
        etag: Optional[str] = None,
        deleted: int = 0,
        created_time: Optional[str] = None,
        creator: Optional[int] = None,
        attachments: Optional[List[Dict]] = None,
        column_id: str = "",
        kind: str = "TEXT",
        img_mode: int = 0,
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
            sort_order: 排序顺序
            time_zone: 时区
            is_floating: 是否浮动
            is_all_day: 是否全天
            reminder: 提醒
            reminders: 提醒列表
            repeat_flag: 重复标记
            ex_date: 排除日期
            items: 子项目
            progress: 进度
            modified_time: 修改时间
            etag: 标签
            deleted: 删除标记
            created_time: 创建时间
            creator: 创建者
            attachments: 附件
            column_id: 列ID
            kind: 类型
            img_mode: 图片模式
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
        self.sort_order = sort_order
        self.time_zone = time_zone
        self.is_floating = is_floating
        self.is_all_day = is_all_day
        self.reminder = reminder
        self.reminders = reminders or []
        self.repeat_flag = repeat_flag
        self.ex_date = ex_date or []
        self.items = items or []
        self.progress = progress
        self.modified_time = self._parse_datetime(modified_time)
        self.etag = etag
        self.deleted = deleted
        self.created_time = self._parse_datetime(created_time)
        self.creator = creator
        self.attachments = attachments or []
        self.column_id = column_id
        self.kind = kind
        self.img_mode = img_mode
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
            sort_order=data.get('sortOrder', 0),
            time_zone=data.get('timeZone', 'Asia/Shanghai'),
            is_floating=data.get('isFloating', False),
            is_all_day=data.get('isAllDay', False),
            reminder=data.get('reminder', ''),
            reminders=data.get('reminders', []),
            repeat_flag=data.get('repeatFlag', ''),
            ex_date=data.get('exDate', []),
            items=data.get('items', []),
            progress=data.get('progress', 0),
            modified_time=data.get('modifiedTime'),
            etag=data.get('etag'),
            deleted=data.get('deleted', 0),
            created_time=data.get('createdTime'),
            creator=data.get('creator'),
            attachments=data.get('attachments', []),
            column_id=data.get('columnId', ''),
            kind=data.get('kind', 'TEXT'),
            img_mode=data.get('imgMode', 0),
            id=data.get('id')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将任务转换为API请求数据
        
        Returns:
            Dict: API请求数据
        """
        data = {
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'status': self.status,
            'sortOrder': self.sort_order,
            'timeZone': self.time_zone,
            'isFloating': self.is_floating,
            'isAllDay': self.is_all_day,
            'reminder': self.reminder,
            'reminders': self.reminders,
            'repeatFlag': self.repeat_flag,
            'exDate': self.ex_date,
            'items': self.items,
            'progress': self.progress,
            'kind': self.kind,
            'imgMode': self.img_mode
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
        if self.modified_time:
            data['modifiedTime'] = self.modified_time.strftime("%Y-%m-%dT%H:%M:%S.000+0000")
        if self.created_time:
            data['createdTime'] = self.created_time.strftime("%Y-%m-%dT%H:%M:%S.000+0000")
        if self.etag:
            data['etag'] = self.etag
        if self.creator:
            data['creator'] = self.creator
        if self.attachments:
            data['attachments'] = self.attachments
        if self.column_id:
            data['columnId'] = self.column_id
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