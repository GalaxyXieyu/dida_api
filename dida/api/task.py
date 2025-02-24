"""
任务和笔记相关API
"""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from .base import BaseAPI
from ..models.task import Task
import pytz

class TaskAPI(BaseAPI):
    """任务和笔记相关的API实现"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._completed_columns = set()  # 存储已完成状态的栏目ID
        self._column_info = {}  # 存储栏目信息
        
    def _update_column_info(self, projects: List[Dict[str, Any]]) -> None:
        """
        更新栏目信息
        
        Args:
            projects: 项目列表数据
        """
        for project in projects:
            if 'columns' in project:
                for column in project['columns']:
                    self._column_info[column['id']] = column
                    # 根据栏目名称或其他特征判断是否为已完成栏目
                    if '已完成' in column.get('name', ''):
                        self._completed_columns.add(column['id'])
    
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
        简化任务数据，只保留必要字段。对于全天任务（时间为00:00:00），只调整截止时间到第二天00:00:00。
        
        Args:
            task_data: 原始任务数据
            
        Returns:
            Dict[str, Any]: 简化后的任务数据
        """
        # 处理日期格式
        def format_date(date_str: Optional[str], is_due_date: bool = False) -> Optional[str]:
            if not date_str:
                return None
            try:
                # 统一处理时区
                local_tz = pytz.timezone('Asia/Shanghai')
                
                # 处理不同格式的时间字符串
                if 'T' in date_str:
                    # 移除毫秒部分，统一时间格式
                    base_time = date_str.split('.')[0]
                    
                    if date_str.endswith('Z'):
                        # 处理 UTC 时间格式 (以Z结尾)
                        dt = datetime.strptime(base_time, "%Y-%m-%dT%H:%M:%S")
                        dt = pytz.UTC.localize(dt)
                    elif '+0000' in date_str:
                        # 处理 UTC 时间格式 (以+0000结尾)
                        dt = datetime.strptime(base_time, "%Y-%m-%dT%H:%M:%S")
                        dt = pytz.UTC.localize(dt)
                    else:
                        # 其他ISO格式时间，尝试多种格式
                        try:
                            # 尝试解析带时区的格式
                            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        except ValueError:
                            # 如果失败，尝试不带时区的格式
                            dt = datetime.strptime(base_time, "%Y-%m-%dT%H:%M:%S")
                            dt = local_tz.localize(dt)
                else:
                    # 处理普通格式时间字符串
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    dt = local_tz.localize(dt)
                
                # 转换为北京时间
                local_dt = dt.astimezone(local_tz)
                
                # 只对截止时间进行调整：如果是截止时间且时间为00:00:00，将日期调整到第二天
                if is_due_date and local_dt.hour == 0 and local_dt.minute == 0 and local_dt.second == 0:
                    local_dt = local_dt + timedelta(days=1)
                
                return local_dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                # 如果所有尝试都失败，尝试解析其他可能的格式
                try:
                    # 处理特殊格式：2025-02-15T02:12:48.001 (不带时区信息)
                    if 'T' in date_str:
                        base_time = date_str.split('.')[0]
                        dt = datetime.strptime(base_time, "%Y-%m-%dT%H:%M:%S")
                        dt = local_tz.localize(dt)
                        local_dt = dt.astimezone(local_tz)
                        
                        # 只对截止时间进行调整
                        if is_due_date and local_dt.hour == 0 and local_dt.minute == 0 and local_dt.second == 0:
                            local_dt = local_dt + timedelta(days=1)
                            
                        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    # 如果还是失败，返回原始字符串，但不打印warning
                    return date_str
                    
        # 处理子任务
        children = []
        if task_data.get('items'):
            for item in task_data['items']:
                # 递归处理每个子任务
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
            'items': children,  # 使用处理后的子任务列表
            'progress': task_data.get('progress', 0),
            'modifiedTime': format_date(task_data.get('modifiedTime')),
            'createdTime': format_date(task_data.get('createdTime')),
            'completedTime': format_date(task_data.get('completedTime')),
            'completedUserId': task_data.get('completedUserId'),
            'isCompleted': task_data.get('isCompleted', False),
            'creator': task_data.get('creator'),
            'timeZone': 'Asia/Shanghai',  # 固定使用北京时区
            'isFloating': task_data.get('isFloating', False),
            'reminders': task_data.get('reminders', []),
            'exDate': task_data.get('exDate', []),
            'etag': task_data.get('etag'),
            'deleted': task_data.get('deleted', 0),
            'attachments': task_data.get('attachments', []),
            'imgMode': task_data.get('imgMode', 0),
            'sortOrder': task_data.get('sortOrder', 0),
            'parentId': task_data.get('parentId'),  # 保留父任务ID
            'children': children  # 添加处理后的子任务列表
        }
        
        return {k: v for k, v in essential_fields.items() if v is not None}
    
    def _get_completed_tasks_info(self) -> Dict[str, Any]:
        """
        获取所有已完成任务的信息
        
        Returns:
            Dict[str, Any]: 包含已完成任务信息的字典，使用 "creator_title" 作为键
        """
        completed_tasks_info = {}
        
        # 获取所有项目
        projects = self._get("/api/v2/batch/check/0").get('projectProfiles', [])
        
        # 遍历每个项目获取已完成的任务
        for project in projects:
            project_id = project['id']
            completed_tasks = self._get(f"/api/v2/project/{project_id}/completed/")
            
            # 将已完成任务的完整信息存储到字典中
            for task in completed_tasks:
                # 使用 creator + title 组合作为键
                key = f"{task.get('creator')}_{task.get('title')}"
                # 确保任务状态为已完成
                task['status'] = 2
                task['isCompleted'] = True
                # 确保有completedTime和completedUserId
                if not task.get('completedTime'):
                    task['completedTime'] = task.get('modifiedTime')
                if not task.get('completedUserId'):
                    task['completedUserId'] = task.get('creator')
                completed_tasks_info[key] = task
                
        return completed_tasks_info
    
    def _is_task_completed(self, task: Dict[str, Any]) -> bool:
        """
        判断任务是否已完成
        
        Args:
            task: 任务数据
            
        Returns:
            bool: 是否已完成
        """
        # 检查任务状态
        if task.get('status') == 2 or task.get('isCompleted', False):
            return True
        
        # 检查是否在已完成栏目中
        if task.get('columnId') in self._completed_columns:
            return True
        
        return False
    
    def get_all_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        获取所有任务（不包含笔记），并组织成树形结构
        
        Args:
            filters: 筛选条件
            
        Returns:
            List[Dict[str, Any]]: 树形结构的任务列表
        """
        tasks = self._get_all_tasks_flat(filters)
        return self.build_task_tree(tasks)

    def _get_all_tasks_flat(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        获取所有任务的扁平列表（内部使用）
        
        Args:
            filters: 筛选条件
                
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        # 获取batch数据
        response = self._get("/api/v2/batch/check/0")
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        projects = response.get('projectProfiles', [])
        tags = response.get('tags', [])
        
        # 更新栏目信息
        self._update_column_info(projects)
        
        # 获取所有已完成任务的信息
        completed_tasks_info = self._get_completed_tasks_info()
            
        # 只处理任务类型
        tasks = []
        for task in tasks_data:
            if task.get('kind') == 'TEXT':
                # 合并项目和标签信息
                task = self._merge_project_info(task, projects)
                task = self._merge_tag_info(task, tags)
                
                # 使用 creator + title 组合来匹配已完成任务
                key = f"{task.get('creator')}_{task.get('title')}"
                
                if key in completed_tasks_info:
                    # 获取完整的已完成任务信息并更新
                    completed_task = completed_tasks_info[key]
                    # 保留原始任务的某些字段
                    original_fields = {
                        'id': task.get('id'),
                        'projectId': task.get('projectId'),
                        'columnId': task.get('columnId'),
                        'sortOrder': task.get('sortOrder'),
                        'tags': task.get('tags', []),
                        'tagDetails': task.get('tagDetails', [])
                    }
                    # 更新任务信息
                    task.update(completed_task)
                    # 恢复原始字段
                    task.update(original_fields)
                else:
                    # 如果任务不在已完成列表中，确保其状态正确
                    task['isCompleted'] = False
                    if task.get('status') == 2:
                        task['status'] = 0
                
                # 简化数据结构
                simplified_task = self._simplify_task_data(task)
                tasks.append(simplified_task)
        
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
    
    def _process_repeat_rule(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理任务的重复规则，支持中文规则名称
        
        Args:
            task_data: 任务数据
            
        Returns:
            Dict[str, Any]: 处理后的任务数据
        """
        if not task_data.get('repeatFlag'):
            return task_data
            
        # 确保有开始时间
        if not task_data.get('startDate'):
            task_data['startDate'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000+0000")
            
        # 如果没有设置第一次重复时间，使用开始时间
        if not task_data.get('repeatFirstDate'):
            task_data['repeatFirstDate'] = task_data.get('startDate')
            
        # 处理不同类型的重复规则
        repeat_flag = task_data['repeatFlag']
        
        # 从开始时间获取日期信息
        start_date = datetime.strptime(task_data['startDate'], "%Y-%m-%dT%H:%M:%S.000+0000")
        current_day = start_date.day
        current_month = start_date.month
        
        # 中文规则映射
        if repeat_flag == '每天':
            task_data.update({
                'repeatFlag': "RRULE:FREQ=DAILY;INTERVAL=1",
                'repeatFrom': "2"
            })
        elif repeat_flag == '每周':  # 每周重复，使用开始日期的星期几
            weekdays = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']
            weekday = weekdays[start_date.weekday()]
            task_data.update({
                'repeatFlag': f"RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY={weekday}",
                'repeatFrom': "2"
            })
        elif repeat_flag == '每月':  # 每月重复，使用开始日期的日期
            task_data.update({
                'repeatFlag': f"RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY={current_day}",
                'repeatFrom': "2"
            })
        elif repeat_flag == '每年':  # 每年重复，使用开始日期的月份和日期
            task_data.update({
                'repeatFlag': f"RRULE:FREQ=YEARLY;INTERVAL=1;BYMONTH={current_month};BYMONTHDAY={current_day}",
                'repeatFrom': "2"
            })
        elif repeat_flag == '每周工作日' or repeat_flag == 'WEEKDAY':
            task_data.update({
                'repeatFlag': "RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR",
                'repeatFrom': "2"
            })
        elif repeat_flag == '法定工作日' or repeat_flag == 'WORKDAY':
            task_data.update({
                'repeatFlag': "RRULE:FREQ=DAILY;INTERVAL=1;TT_SKIP=HOLIDAY,WEEKEND",
                'repeatFrom': "2"
            })
        elif repeat_flag == '艾宾浩斯记忆法' or repeat_flag == 'FORGETTINGCURVE':
            task_data.update({
                'repeatFlag': "ERULE:NAME=FORGETTINGCURVE;CYCLE=0",
                'repeatFrom': "0"
            })
        elif repeat_flag.startswith('RRULE:') or repeat_flag.startswith('ERULE:'):
            # 自定义规则，保持原样
            if 'repeatFrom' not in task_data:
                task_data['repeatFrom'] = "2"
                
        return task_data
    
    def create_task(self, task_data: Dict[str, Any], parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        创建新任务，支持子任务创建和艾宾浩斯记忆曲线重复模式
        
        Args:
            task_data: 任务数据
            parent_id: 父任务ID（如果是子任务）
            
        Returns:
            Dict[str, Any]: 创建成功的任务
        """
        # 设置任务类型
        if 'items' in task_data:
            task_data['kind'] = 'CHECKLIST'
        else:
            task_data['kind'] = 'TEXT'
            
        # 设置时区为北京时间
        task_data['timeZone'] = 'Asia/Shanghai'
        
        # 处理时间格式
        def convert_to_utc(local_time_str: str) -> str:
            try:
                # 解析本地时间字符串
                local_tz = pytz.timezone('Asia/Shanghai')
                if 'T' in local_time_str:
                    # 如果已经是ISO格式，先转换为本地时间
                    dt = datetime.fromisoformat(local_time_str.replace('Z', '+00:00'))
                    if dt.tzinfo is None:
                        dt = local_tz.localize(dt)
                else:
                    # 普通格式时间字符串，作为本地时间处理
                    dt = datetime.strptime(local_time_str, "%Y-%m-%d %H:%M:%S")
                    dt = local_tz.localize(dt)
                
                # 转换为UTC时间
                utc_dt = dt.astimezone(pytz.UTC)
                return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            except Exception as e:
                print(f"Warning: Failed to convert time to UTC: {e}")
                return local_time_str
        
        # 处理开始时间和结束时间
        if 'startDate' in task_data:
            task_data['startDate'] = convert_to_utc(task_data['startDate'])
        if 'dueDate' in task_data:
            task_data['dueDate'] = convert_to_utc(task_data['dueDate'])
            
        # 处理重复规则
        task_data = self._process_repeat_rule(task_data)
                
        # 创建任务
        response = self._post("/api/v2/task", task_data)
        created_task = self._simplify_task_data(response)
        
        # 如果是子任务，关联到父任务
        if parent_id:
            self.link_subtask(created_task['id'], parent_id, task_data.get('projectId'))
            
        return created_task
    
    def create_subtask(self, parent_id: str, subtask_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建子任务并关联到父任务
        
        Args:
            parent_id: 父任务ID
            subtask_data: 子任务数据
            
        Returns:
            Dict[str, Any]: 创建成功的子任务
        """
        # 获取父任务信息以获取projectId
        parent_task = self.get_task(parent_id)
        subtask_data['projectId'] = parent_task['projectId']
        
        # 创建子任务
        return self.create_task(subtask_data, parent_id)
    
    def link_subtask(self, task_id: str, parent_id: str, project_id: str) -> bool:
        """
        将任务关联为另一个任务的子任务
        
        Args:
            task_id: 子任务ID
            parent_id: 父任务ID
            project_id: 项目ID
            
        Returns:
            bool: 是否关联成功
        """
        data = [{
            "taskId": task_id,
            "projectId": project_id,
            "parentId": parent_id
        }]
        
        response = self._post("/api/v2/batch/taskParent", data)
        return bool(response)
    
    def create_forgetting_curve_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建基于艾宾浩斯记忆曲线的重复任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            Dict[str, Any]: 创建成功的任务
        """
        # 设置艾宾浩斯记忆曲线重复模式
        task_data.update({
            'repeatFlag': 'FORGETTINGCURVE',
            'repeatFrom': "0",
            'isFloating': False,
            'timeZone': task_data.get('timeZone', 'Asia/Shanghai')
        })
        
        return self.create_task(task_data)
    
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
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        统一解析日期字符串为datetime对象
        
        Args:
            date_str: 日期字符串
            
        Returns:
            Optional[datetime]: 解析后的datetime对象，解析失败返回None
        """
        if not date_str:
            return None
            
        try:
            # 尝试ISO格式
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.000+0000")
        except ValueError:
            try:
                # 尝试标准格式
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"Warning: Unrecognized date format: {date_str}")
                return None
    
    def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime, include_completed: bool = True) -> List[Dict[str, Any]]:
        """
        获取指定日期范围内的任务
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            include_completed: 是否包含已完成的任务
            
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        tasks = self.get_all_tasks()
        filtered_tasks = []
        
        for task in tasks:
            # 优先使用开始时间，如果没有则使用截止时间
            task_date = self._parse_date(task.get('startDate')) or self._parse_date(task.get('dueDate'))
            if task_date and start_date <= task_date <= end_date:
                if include_completed or task.get('status') != 2:
                    filtered_tasks.append(task)
                    
        return filtered_tasks
    
    def get_today_tasks(self, include_completed: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取今天的任务，按完成状态分组，并组织成树形结构
        
        Args:
            include_completed: 是否包含已完成的任务
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的树形结构任务
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        # 获取所有任务
        all_tasks = self._get_all_tasks_flat()
        uncompleted_tasks = []
        completed_tasks = []
        
        for task in all_tasks:
            task_date = self._parse_date(task.get('startDate')) or self._parse_date(task.get('dueDate'))
            if task_date and today <= task_date < tomorrow:
                if self._is_task_completed(task):
                    if include_completed:
                        completed_tasks.append(task)
                else:
                    uncompleted_tasks.append(task)
                
        return {
            'completed': self.build_task_tree(completed_tasks),
            'uncompleted': self.build_task_tree(uncompleted_tasks)
        }
    
    def get_this_week_tasks(self, include_completed: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取本周的任务，按完成状态分组，并组织成树形结构
        
        Args:
            include_completed: 是否包含已完成的任务
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的树形结构任务
        """
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        next_monday = monday + timedelta(days=7)
        
        # 获取所有未完成任务
        uncompleted_tasks = self._get_all_tasks_flat()
        
        # 如果需要包含已完成任务，则获取本周完成的任务
        completed_tasks = []
        if include_completed:
            for project in self._get("/api/v2/batch/check/0").get('projectProfiles', []):
                project_completed = self.get_completed_tasks(
                    project['id'],
                    from_time=monday.strftime("%Y-%m-%d %H:%M:%S"),
                    to_time=next_monday.strftime("%Y-%m-%d %H:%M:%S")
                )
                completed_tasks.extend(project_completed)
        
        # 过滤本周的任务
        week_tasks = []
        for task in uncompleted_tasks:
            task_date = self._parse_date(task.get('startDate')) or self._parse_date(task.get('dueDate'))
            if task_date and monday <= task_date < next_monday:
                week_tasks.append(task)
                
        return {
            'completed': self.build_task_tree(completed_tasks),
            'uncompleted': self.build_task_tree(week_tasks)
        }
    
    def get_this_month_tasks(self, include_completed: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取本月的任务，按完成状态分组，并组织成树形结构
        
        Args:
            include_completed: 是否包含已完成的任务
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的树形结构任务
        """
        today = datetime.now()
        first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if today.month == 12:
            next_first_day = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_first_day = today.replace(month=today.month + 1, day=1)
            
        # 获取所有未完成任务
        uncompleted_tasks = self._get_all_tasks_flat()
        
        # 如果需要包含已完成任务，则获取本月完成的任务
        completed_tasks = []
        if include_completed:
            for project in self._get("/api/v2/batch/check/0").get('projectProfiles', []):
                project_completed = self.get_completed_tasks(
                    project['id'],
                    from_time=first_day.strftime("%Y-%m-%d %H:%M:%S"),
                    to_time=next_first_day.strftime("%Y-%m-%d %H:%M:%S")
                )
                completed_tasks.extend(project_completed)
        
        # 过滤本月的任务
        month_tasks = []
        for task in uncompleted_tasks:
            task_date = self._parse_date(task.get('startDate')) or self._parse_date(task.get('dueDate'))
            if task_date and first_day <= task_date < next_first_day:
                month_tasks.append(task)
                
        return {
            'completed': self.build_task_tree(completed_tasks),
            'uncompleted': self.build_task_tree(month_tasks)
        }
    
    def get_next_7_days_tasks(self, include_completed: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取未来7天的任务，按完成状态分组，并组织成树形结构
        
        Args:
            include_completed: 是否包含已完成的任务
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的树形结构任务
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        next_week = today + timedelta(days=7)
        
        tasks = self.get_tasks_by_date_range(today, next_week, include_completed)
        grouped_tasks = self._group_tasks_by_status(tasks)
        return {
            'completed': self.build_task_tree(grouped_tasks['completed']),
            'uncompleted': self.build_task_tree(grouped_tasks['uncompleted'])
        }
    
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有已过期但未完成的任务，并组织成树形结构。
        对于全天任务（时间为00:00:00的任务），将在第二天才会被判定为过期。

        Returns:
            List[Dict[str, Any]]: 树形结构的过期任务列表
        """
        now = datetime.now()
        tasks = self._get_all_tasks_flat()
        overdue_tasks = []
        
        for task in tasks:
            if task.get('status') != 2:  # 未完成
                due_date = self._parse_date(task.get('dueDate'))
                if due_date:
                    # 检查是否是全天任务（时间为00:00:00）
                    is_all_day = (due_date.hour == 0 and due_date.minute == 0 and due_date.second == 0)
                    
                    if is_all_day:
                        # 全天任务：如果当前时间超过了第二天的00:00:00，则任务过期
                        next_day = due_date + timedelta(days=1)
                        if now >= next_day:
                            overdue_tasks.append(task)
                    else:
                        # 非全天任务：如果当前时间超过了截止时间，则任务过期
                        if now > due_date:
                            overdue_tasks.append(task)
                    
        return self.build_task_tree(overdue_tasks)
    
    def get_tasks_by_priority(self, priority: int = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取指定优先级的任务，按完成状态分组，并组织成树形结构
        
        Args:
            priority: 优先级 (0-最低, 1-低, 3-中, 5-高)，None表示获取所有优先级
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的树形结构任务
        """
        tasks = self._get_all_tasks_flat()
        if priority is not None:
            tasks = [task for task in tasks if task.get('priority') == priority]
        grouped_tasks = self._group_tasks_by_status(tasks)
        return {
            'completed': self.build_task_tree(grouped_tasks['completed']),
            'uncompleted': self.build_task_tree(grouped_tasks['uncompleted'])
        }
    
    def _group_tasks_by_status(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        按状态分组任务
        
        Args:
            tasks: 任务列表
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 分组后的任务
        """
        completed_tasks = []
        uncompleted_tasks = []
        
        for task in tasks:
            if self._is_task_completed(task):
                completed_tasks.append(task)
            else:
                uncompleted_tasks.append(task)
                
        return {
            'completed': completed_tasks,
            'uncompleted': uncompleted_tasks
        }
        
    def get_task_statistics(self) -> Dict[str, Any]:
        """
        获取任务统计信息
        
        Returns:
            Dict[str, Any]: 统计信息，包括：
                - 总任务数
                - 已完成任务数
                - 未完成任务数
                - 过期任务数
                - 各优先级任务数
                - 今日完成率
                - 本周完成率
                - 本月完成率
        """
        # 获取所有未完成任务
        uncompleted_tasks = self.get_all_tasks()
        
        # 获取所有已完成任务
        completed_tasks = []
        for project in self._get("/api/v2/batch/check/0").get('projectProfiles', []):
            project_completed = self.get_completed_tasks(project['id'])
            completed_tasks.extend(project_completed)
            
        # 获取过期任务
        overdue_tasks = self.get_overdue_tasks()
        
        # 按优先级统计
        all_tasks = uncompleted_tasks + completed_tasks
        priority_stats = {
            '最低': len([t for t in all_tasks if t.get('priority') == 0]),
            '低': len([t for t in all_tasks if t.get('priority') == 1]),
            '中': len([t for t in all_tasks if t.get('priority') == 3]),
            '高': len([t for t in all_tasks if t.get('priority') == 5])
        }
        
        # 计算完成率
        today_tasks = self.get_today_tasks()
        this_week_tasks = self.get_this_week_tasks()
        this_month_tasks = self.get_this_month_tasks()
        
        def calculate_completion_rate(tasks):
            completed = len(tasks.get('completed', []))
            total = completed + len(tasks.get('uncompleted', []))
            return round(completed / total * 100, 2) if total > 0 else 0
        
        return {
            'total_tasks': len(all_tasks),
            'completed_tasks': len(completed_tasks),
            'uncompleted_tasks': len(uncompleted_tasks),
            'overdue_tasks': len(overdue_tasks),
            'priority_stats': priority_stats,
            'today_completion_rate': calculate_completion_rate(today_tasks),
            'week_completion_rate': calculate_completion_rate(this_week_tasks),
            'month_completion_rate': calculate_completion_rate(this_month_tasks)
        }
    
    def get_task_trends(self, days: int = 30) -> Dict[str, List[Any]]:
        """
        获取任务趋势数据
        
        Args:
            days: 统计天数
            
        Returns:
            Dict[str, List[Any]]: 趋势数据，包括：
                - dates: 日期列表
                - completed_counts: 每日完成数
                - created_counts: 每日新建数
                - completion_rates: 每日完成率
        """
        end_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = (end_date - timedelta(days=days-1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        all_tasks = self.get_all_tasks()
        dates = []
        completed_counts = []
        created_counts = []
        completion_rates = []
        
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # 统计当日完成的任务
            completed = len([
                task for task in all_tasks
                if task.get('status') == 2
                and datetime.strptime(task.get('modifiedTime'), "%Y-%m-%dT%H:%M:%S.000+0000").date() == current_date.date()
            ])
            
            # 统计当日创建的任务
            created = len([
                task for task in all_tasks
                if datetime.strptime(task.get('createdTime'), "%Y-%m-%dT%H:%M:%S.000+0000").date() == current_date.date()
            ])
            
            # 计算完成率
            rate = round(completed / created * 100, 2) if created > 0 else 0
            
            dates.append(current_date.strftime('%Y-%m-%d'))
            completed_counts.append(completed)
            created_counts.append(created)
            completion_rates.append(rate)
            
            current_date = next_date
            
        return {
            'dates': dates,
            'completed_counts': completed_counts,
            'created_counts': created_counts,
            'completion_rates': completion_rates
        }
    
    def get_completed_tasks(self, project_id: Optional[str] = None, limit: int = 50, from_time: Optional[str] = None, to_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取已完成的任务。如果不指定project_id，则获取所有项目的已完成任务
        
        Args:
            project_id: 项目ID（可选）。如果不指定，则获取所有项目的已完成任务
            limit: 返回的任务数量限制
            from_time: 开始时间，格式为 "2025-02-19 14:44:46"
            to_time: 结束时间，格式为 "2025-02-19 14:44:46"
            
        Returns:
            List[Dict[str, Any]]: 已完成的任务列表
        """
        completed_tasks = []
        
        # 如果没有指定project_id，获取所有项目
        if project_id is None:
            projects = self._get("/api/v2/batch/check/0").get('projectProfiles', [])
            project_ids = [p['id'] for p in projects]
        else:
            project_ids = [project_id]
        
        # 遍历所有项目获取已完成任务
        for pid in project_ids:
            params = {'limit': limit}
            if from_time:
                params['from'] = from_time
            if to_time:
                params['to'] = to_time
            
            response = self._get(f"/api/v2/project/{pid}/completed/", params=params)
            completed_tasks.extend(response)
        
        # 简化数据结构
        return [self._simplify_task_data(task) for task in completed_tasks]

    def build_task_tree(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将任务列表转换为树形结构
        
        Args:
            tasks: 任务列表
            
        Returns:
            List[Dict[str, Any]]: 树形结构的任务列表
        """
        # 创建任务ID到任务的映射
        task_map = {task['id']: task for task in tasks}
        
        # 初始化每个任务的children列表
        for task in tasks:
            task['children'] = []
        
        # 构建树形结构
        root_tasks = []
        for task in tasks:
            parent_id = task.get('parentId')
            if parent_id and parent_id in task_map:
                # 如果有父任务，将当前任务添加到父任务的children中
                task_map[parent_id]['children'].append(task)
            else:
                # 如果没有父任务，则为根任务
                root_tasks.append(task)
        
        return root_tasks

    def get_this_week_tasks_with_tree(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取本周的任务，按完成状态分组，并组织成树形结构
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的树形结构任务
        """
        tasks = self.get_this_week_tasks()
        return {
            'completed': self.build_task_tree(tasks['completed']),
            'uncompleted': self.build_task_tree(tasks['uncompleted'])
        }
        
    def get_today_tasks_with_tree(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取今天的任务，按完成状态分组，并组织成树形结构
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的树形结构任务
        """
        tasks = self.get_today_tasks()
        return {
            'completed': self.build_task_tree(tasks['completed']),
            'uncompleted': self.build_task_tree(tasks['uncompleted'])
        }
        
    def get_this_month_tasks_with_tree(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取本月的任务，按完成状态分组，并组织成树形结构
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的树形结构任务
        """
        tasks = self.get_this_month_tasks()
        return {
            'completed': self.build_task_tree(tasks['completed']),
            'uncompleted': self.build_task_tree(tasks['uncompleted'])
        }
        
    def get_next_7_days_tasks_with_tree(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取未来7天的任务，按完成状态分组，并组织成树形结构
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的树形结构任务
        """
        tasks = self.get_next_7_days_tasks()
        return {
            'completed': self.build_task_tree(tasks['completed']),
            'uncompleted': self.build_task_tree(tasks['uncompleted'])
        }
        
    def get_tasks_by_priority_with_tree(self, priority: int = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取指定优先级的任务，按完成状态分组，并组织成树形结构
        
        Args:
            priority: 优先级 (0-最低, 1-低, 3-中, 5-高)，None表示获取所有优先级
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的树形结构任务
        """
        tasks = self.get_tasks_by_priority(priority)
        return {
            'completed': self.build_task_tree(tasks['completed']),
            'uncompleted': self.build_task_tree(tasks['uncompleted'])
        }
        
    def get_overdue_tasks_with_tree(self) -> List[Dict[str, Any]]:
        """
        获取所有已过期但未完成的任务，并组织成树形结构
        
        Returns:
            List[Dict[str, Any]]: 树形结构的过期任务列表
        """
        tasks = self.get_overdue_tasks()
        return self.build_task_tree(tasks)

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
            # 基础筛选
            if key == 'status' and item.get('status') != value:
                return False
            elif key == 'priority' and item.get('priority') != value:
                return False
            elif key == 'project_id' and item.get('projectId') != value:
                return False
            elif key == 'project_name' and value.lower() not in item.get('projectName', '').lower():
                return False
            elif key == 'column_id' and item.get('columnId') != value:
                return False
            
            # 标签筛选
            elif key == 'tag_names':
                if isinstance(value, str):  # 如果是单个标签
                    value = [value]
                item_tags = {tag['name'].lower() for tag in item.get('tagDetails', [])}
                # 检查是否包含任意一个标签（OR关系）
                if not any(tag.lower() in item_tags for tag in value):
                    return False
            elif key == 'tag_names_all':  # 必须包含所有指定标签（AND关系）
                if isinstance(value, str):
                    value = [value]
                item_tags = {tag['name'].lower() for tag in item.get('tagDetails', [])}
                # 检查是否包含所有标签
                if not all(tag.lower() in item_tags for tag in value):
                    return False
            
            # 日期筛选
            elif key == 'start_date' and item.get('startDate'):
                item_date = self._parse_date(item['startDate'])
                filter_date = self._parse_date(value)
                if not item_date or not filter_date or item_date < filter_date:
                    return False
            elif key == 'due_date' and item.get('dueDate'):
                item_date = self._parse_date(item['dueDate'])
                filter_date = self._parse_date(value)
                if not item_date or not filter_date or item_date > filter_date:
                    return False
            elif key == 'has_due_date' and bool(item.get('dueDate')) != value:
                return False
            elif key == 'has_start_date' and bool(item.get('startDate')) != value:
                return False
            
            # 完成状态筛选
            elif key == 'is_completed' and item.get('isCompleted') != value:
                return False
            
            # 进度筛选
            elif key == 'min_progress' and item.get('progress', 0) < value:
                return False
            elif key == 'max_progress' and item.get('progress', 0) > value:
                return False
            
            # 模糊搜索
            elif key == 'keyword':
                keyword = str(value).lower()
                title = item.get('title', '').lower()
                content = item.get('content', '').lower()
                project_name = item.get('projectName', '').lower()
                tags = ' '.join(tag['name'].lower() for tag in item.get('tagDetails', []))
                if keyword not in title and keyword not in content and keyword not in project_name and keyword not in tags:
                    return False
            
            # 创建时间筛选
            elif key == 'created_after' and item.get('createdTime'):
                item_date = self._parse_date(item['createdTime'])
                filter_date = self._parse_date(value)
                if not item_date or not filter_date or item_date < filter_date:
                    return False
            elif key == 'created_before' and item.get('createdTime'):
                item_date = self._parse_date(item['createdTime'])
                filter_date = self._parse_date(value)
                if not item_date or not filter_date or item_date > filter_date:
                    return False
            
            # 修改时间筛选
            elif key == 'modified_after' and item.get('modifiedTime'):
                item_date = self._parse_date(item['modifiedTime'])
                filter_date = self._parse_date(value)
                if not item_date or not filter_date or item_date < filter_date:
                    return False
            elif key == 'modified_before' and item.get('modifiedTime'):
                item_date = self._parse_date(item['modifiedTime'])
                filter_date = self._parse_date(value)
                if not item_date or not filter_date or item_date > filter_date:
                    return False
            
            # 子任务筛选
            elif key == 'has_items' and bool(item.get('items')) != value:
                return False
            elif key == 'min_items' and len(item.get('items', [])) < value:
                return False
            elif key == 'max_items' and len(item.get('items', [])) > value:
                return False
            
        return True 