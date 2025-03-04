"""
滴答清单 API 模块

这个模块提供了与滴答清单 API 交互的各种功能类和工具。

主要组件:
- TaskAPI: 任务管理相关的 API
- ProjectAPI: 项目管理相关的 API
- TagAPI: 标签管理相关的 API
- BaseAPI: API 基础类
"""

from .base import BaseAPI
from .tasks import TaskAPI, ReminderOption
from .project import ProjectAPI
from .tag import TagAPI

__all__ = [
    'BaseAPI',
    'TaskAPI',
    'ProjectAPI',
    'TagAPI',
    'ReminderOption',
]

__version__ = '1.0.0'
