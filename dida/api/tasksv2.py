"""
任务API版本2，支持灵活的任务查询功能
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pytz
from .base import BaseAPI

class TaskAPI(BaseAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._completed_columns = set()  # 存储已完成状态的栏目ID
        self._column_info = {}  # 存储栏目信息

    def get_tasks(self, mode: str = "all", keyword: Optional[str] = None, priority: Optional[int] = None,
                  project_name: Optional[str] = None, tag_names: Optional[List[str]] = None,
                  created_after: Optional[datetime] = None, created_before: Optional[datetime] = None,
                  completed_after: Optional[datetime] = None, completed_before: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取任务，支持多种模式和筛选条件
        
        Args:
            mode: 查询模式，支持 "all", "today", "yesterday", "recent_7_days"
            keyword: 关键词筛选
            priority: 优先级筛选 (0-最低, 1-低, 3-中, 5-高)
            project_name: 项目名称筛选
            tag_names: 标签名称列表筛选
            created_after: 创建时间开始筛选
            created_before: 创建时间结束筛选
            completed_after: 完成时间开始筛选
            completed_before: 完成时间结束筛选
            
        Returns:
            List[Dict[str, Any]]: 符合条件的任务列表
        """
        tasks = self.get_all_tasks()

        if mode == "today":
            tasks = [task for task in tasks if self._is_today(task)]
        elif mode == "yesterday":
            tasks = [task for task in tasks if self._is_yesterday(task)]
        elif mode == "recent_7_days":
            tasks = [task for task in tasks if self._is_recent_7_days(task)]

        if keyword:
            tasks = [task for task in tasks if keyword.lower() in task.get('title', '').lower() or keyword.lower() in task.get('content', '').lower()]
        if priority is not None:
            tasks = [task for task in tasks if task.get('priority') == priority]
        if project_name:
            tasks = [task for task in tasks if project_name.lower() in task.get('projectName', '').lower()]
        if tag_names:
            tasks = [task for task in tasks if any(tag in task.get('tags', []) for tag in tag_names)]
        if created_after:
            tasks = [task for task in tasks if self._parse_date(task.get('createdTime')) >= created_after]
        if created_before:
            tasks = [task for task in tasks if self._parse_date(task.get('createdTime')) <= created_before]
        if completed_after:
            tasks = [task for task in tasks if self._parse_date(task.get('completedTime')) >= completed_after]
        if completed_before:
            tasks = [task for task in tasks if self._parse_date(task.get('completedTime')) <= completed_before]

        return tasks

    def _is_today(self, task: Dict[str, Any]) -> bool:
        today = datetime.now().date()
        task_date = self._parse_date(task.get('dueDate')) or self._parse_date(task.get('startDate'))
        return task_date and task_date.date() == today

    def _is_yesterday(self, task: Dict[str, Any]) -> bool:
        yesterday = datetime.now().date() - timedelta(days=1)
        task_date = self._parse_date(task.get('dueDate')) or self._parse_date(task.get('startDate'))
        return task_date and task_date.date() == yesterday

    def _is_recent_7_days(self, task: Dict[str, Any]) -> bool:
        seven_days_ago = datetime.now() - timedelta(days=7)
        task_date = self._parse_date(task.get('dueDate')) or self._parse_date(task.get('startDate'))
        return task_date and task_date >= seven_days_ago

    def _merge_project_info(self, task_data: Dict[str, Any], projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not task_data.get('projectId'):
            return task_data
        for project in projects:
            if project['id'] == task_data['projectId']:
                task_data['projectName'] = project['name']
                task_data['projectKind'] = project['kind']
                break
        return task_data

    def _merge_tag_info(self, task_data: Dict[str, Any], tags: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        def format_date(date_str: Optional[str], is_due_date: bool = False) -> Optional[str]:
            if not date_str:
                return None
            try:
                local_tz = pytz.timezone('Asia/Shanghai')
                if 'T' in date_str:
                    base_time = date_str.split('.')[0]
                    if date_str.endswith('Z'):
                        dt = datetime.strptime(base_time, "%Y-%m-%dT%H:%M:%S")
                        dt = pytz.UTC.localize(dt)
                    elif '+0000' in date_str:
                        dt = datetime.strptime(base_time, "%Y-%m-%dT%H:%M:%S")
                        dt = pytz.UTC.localize(dt)
                    else:
                        try:
                            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        except ValueError:
                            dt = datetime.strptime(base_time, "%Y-%m-%dT%H:%M:%S")
                            dt = local_tz.localize(dt)
                else:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    dt = local_tz.localize(dt)
                local_dt = dt.astimezone(local_tz)
                if is_due_date and local_dt.hour == 0 and local_dt.minute == 0 and local_dt.second == 0:
                    local_dt = local_dt + timedelta(days=1)
                return local_dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                return date_str
        children = []
        if task_data.get('items'):
            for item in task_data['items']:
                child_task = self._simplify_task_data(item)
                children.append(child_task)
        essential_fields = {
            'id': task_data.get('id'),
            'title': task_data.get('title'),
            'content': task_data.get('content'),
            'priority': task_data.get('priority'),
            'status': task_data.get('status'),
            'startDate': format_date(task_data.get('startDate'), is_due_date=False),
            'dueDate': format_date(task_data.get('dueDate'), is_due_date=True),
            'projectName': task_data.get('projectName'),
            'projectId': task_data.get('projectId'),
            'projectKind': task_data.get('projectKind'),
            'columnId': task_data.get('columnId'),
            'tagDetails': task_data.get('tagDetails', []),
            'kind': task_data.get('kind'),
            'isAllDay': task_data.get('isAllDay'),
            'reminder': task_data.get('reminder'),
            'repeatFlag': task_data.get('repeatFlag'),
            'items': children,
            'progress': task_data.get('progress', 0),
            'modifiedTime': format_date(task_data.get('modifiedTime')),
            'createdTime': format_date(task_data.get('createdTime')),
            'completedTime': format_date(task_data.get('completedTime')),
            'completedUserId': task_data.get('completedUserId'),
            'isCompleted': task_data.get('isCompleted', False),
            'creator': task_data.get('creator'),
            'timeZone': 'Asia/Shanghai',
            'isFloating': task_data.get('isFloating', False),
            'reminders': task_data.get('reminders', []),
            'exDate': task_data.get('exDate', []),
            'etag': task_data.get('etag'),
            'deleted': task_data.get('deleted', 0),
            'attachments': task_data.get('attachments', []),
            'imgMode': task_data.get('imgMode', 0),
            'sortOrder': task_data.get('sortOrder', 0),
            'parentId': task_data.get('parentId'),
            'children': children
        }
        return {k: v for k, v in essential_fields.items() if v is not None}

    def _get_completed_tasks_info(self) -> Dict[str, Any]:
        completed_tasks_info = {}
        projects = self._get("/api/v2/batch/check/0").get('projectProfiles', [])
        for project in projects:
            project_id = project['id']
            completed_tasks = self._get(f"/api/v2/project/{project_id}/completed/")
            for task in completed_tasks:
                key = f"{task.get('creator')}_{task.get('title')}"
                task['status'] = 2
                task['isCompleted'] = True
                if not task.get('completedTime'):
                    task['completedTime'] = task.get('modifiedTime')
                if not task.get('completedUserId'):
                    task['completedUserId'] = task.get('creator')
                completed_tasks_info[key] = task
        return completed_tasks_info

    def _is_task_completed(self, task: Dict[str, Any]) -> bool:
        if task.get('status') == 2 or task.get('isCompleted', False):
            return True
        if task.get('columnId') in self._completed_columns:
            return True
        return False

    def get_all_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        tasks = self._get_all_tasks_flat(filters)
        return self.build_task_tree(tasks)

    def _get_all_tasks_flat(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        response = self._get("/api/v2/batch/check/0")
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        projects = response.get('projectProfiles', [])
        tags = response.get('tags', [])
        self._update_column_info(projects)
        completed_tasks_info = self._get_completed_tasks_info()
        tasks = []
        for task in tasks_data:
            if task.get('kind') == 'TEXT':
                task = self._merge_project_info(task, projects)
                task = self._merge_tag_info(task, tags)
                key = f"{task.get('creator')}_{task.get('title')}"
                if key in completed_tasks_info:
                    completed_task = completed_tasks_info[key]
                    original_fields = {
                        'id': task.get('id'),
                        'projectId': task.get('projectId'),
                        'columnId': task.get('columnId'),
                        'sortOrder': task.get('sortOrder'),
                        'tags': task.get('tags', []),
                        'tagDetails': task.get('tagDetails', [])
                    }
                    task.update(completed_task)
                    task.update(original_fields)
                else:
                    task['isCompleted'] = False
                    if task.get('status') == 2:
                        task['status'] = 0
                simplified_task = self._simplify_task_data(task)
                tasks.append(simplified_task)
        if filters:
            filtered_tasks = []
            for task in tasks:
                if self._apply_filters(task, filters):
                    filtered_tasks.append(task)
            return filtered_tasks
        return tasks 