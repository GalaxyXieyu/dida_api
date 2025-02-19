"""
任务和笔记相关API
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .base import BaseAPI
from ..models.task import Task

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
        简化任务数据，只保留必要字段
        
        Args:
            task_data: 原始任务数据
            
        Returns:
            Dict[str, Any]: 简化后的任务数据
        """
        # 处理日期格式
        def format_date(date_str: Optional[str]) -> Optional[str]:
            if not date_str:
                return None
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.000+0000")
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                return date_str

        essential_fields = {
            'id': task_data.get('id'),
            'title': task_data.get('title'),
            'content': task_data.get('content'),
            'priority': task_data.get('priority'),
            'status': task_data.get('status'),
            'startDate': format_date(task_data.get('startDate')),
            'dueDate': format_date(task_data.get('dueDate')),
            'projectName': task_data.get('projectName'),
            'projectId': task_data.get('projectId'),
            'projectKind': task_data.get('projectKind'),
            'columnId': task_data.get('columnId'),
            'tagDetails': task_data.get('tagDetails', []),
            'kind': task_data.get('kind'),
            'isAllDay': task_data.get('isAllDay'),
            'reminder': task_data.get('reminder'),
            'repeatFlag': task_data.get('repeatFlag'),
            'items': task_data.get('items', []),
            'progress': task_data.get('progress', 0),
            'modifiedTime': format_date(task_data.get('modifiedTime')),
            'createdTime': format_date(task_data.get('createdTime')),
            'completedTime': format_date(task_data.get('completedTime')),
            'completedUserId': task_data.get('completedUserId'),
            'isCompleted': task_data.get('isCompleted', False)  # 使用传入的isCompleted值
        }
        
        return {k: v for k, v in essential_fields.items() if v is not None}
    
    def _get_completed_tasks_info(self) -> Dict[str, Any]:
        """
        获取所有已完成任务的信息
        
        Returns:
            Dict[str, Any]: 包含已完成任务ID和完成时间的字典
        """
        completed_tasks_info = {}
        
        # 获取所有项目
        projects = self._get("/api/v2/batch/check/0").get('projectProfiles', [])
        
        # 遍历每个项目获取已完成的任务
        for project in projects:
            project_id = project['id']
            completed_tasks = self._get(f"/api/v2/project/{project_id}/completed/")
            
            # 将已完成任务的信息存储到字典中
            for task in completed_tasks:
                completed_tasks_info[task['id']] = {
                    'completedTime': task.get('completedTime'),
                    'completedUserId': task.get('completedUserId')
                }
                
        return completed_tasks_info
    
    def _is_task_completed(self, task: Dict[str, Any], completed_tasks_info: Dict[str, Any]) -> bool:
        """
        判断任务是否已完成
        
        Args:
            task: 任务数据
            completed_tasks_info: 已完成任务信息字典
            
        Returns:
            bool: 是否已完成
        """
        task_id = task.get('id')
        if task_id in completed_tasks_info:
            # 如果任务ID在已完成任务信息中，则更新任务的完成信息
            task['completedTime'] = completed_tasks_info[task_id].get('completedTime')
            task['completedUserId'] = completed_tasks_info[task_id].get('completedUserId')
            return True
        return False
    
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
                
                # 判断任务是否完成并更新相关信息
                is_completed = self._is_task_completed(task, completed_tasks_info)
                task['isCompleted'] = is_completed
                
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
                if datetime.strptime(item['startDate'], "%Y-%m-%d %H:%M:%S") < datetime.strptime(value, "%Y-%m-%d %H:%M:%S"):
                    return False
            elif key == 'due_date' and item.get('dueDate'):
                if datetime.strptime(item['dueDate'], "%Y-%m-%d %H:%M:%S") > datetime.strptime(value, "%Y-%m-%d %H:%M:%S"):
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
                if datetime.strptime(item['createdTime'], "%Y-%m-%d %H:%M:%S") < datetime.strptime(value, "%Y-%m-%d %H:%M:%S"):
                    return False
            elif key == 'created_before' and item.get('createdTime'):
                if datetime.strptime(item['createdTime'], "%Y-%m-%d %H:%M:%S") > datetime.strptime(value, "%Y-%m-%d %H:%M:%S"):
                    return False
            
            # 修改时间筛选
            elif key == 'modified_after' and item.get('modifiedTime'):
                if datetime.strptime(item['modifiedTime'], "%Y-%m-%d %H:%M:%S") < datetime.strptime(value, "%Y-%m-%d %H:%M:%S"):
                    return False
            elif key == 'modified_before' and item.get('modifiedTime'):
                if datetime.strptime(item['modifiedTime'], "%Y-%m-%d %H:%M:%S") > datetime.strptime(value, "%Y-%m-%d %H:%M:%S"):
                    return False
            
            # 子任务筛选
            elif key == 'has_items' and bool(item.get('items')) != value:
                return False
            elif key == 'min_items' and len(item.get('items', [])) < value:
                return False
            elif key == 'max_items' and len(item.get('items', [])) > value:
                return False
            
        return True
    
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
            task_date = datetime.strptime(task.get('startDate', task.get('dueDate')), "%Y-%m-%dT%H:%M:%S.000+0000") if task.get('startDate') or task.get('dueDate') else None
            if task_date and start_date <= task_date <= end_date:
                if include_completed or task.get('status') != 2:
                    filtered_tasks.append(task)
                    
        return filtered_tasks
    
    def get_today_tasks(self, include_completed: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取今天的任务，按完成状态分组
        
        Args:
            include_completed: 是否包含已完成的任务
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的任务
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        # 获取所有未完成任务
        uncompleted_tasks = []
        all_tasks = self.get_all_tasks()
        for task in all_tasks:
            if not self._is_task_completed(task):
                task_date = datetime.strptime(task.get('startDate', task.get('dueDate')), "%Y-%m-%d %H:%M:%S") if task.get('startDate') or task.get('dueDate') else None
                if task_date and today <= task_date < tomorrow:
                    uncompleted_tasks.append(task)
        
        # 如果需要包含已完成任务，则获取今天完成的任务
        completed_tasks = []
        if include_completed:
            for project in self._get("/api/v2/batch/check/0").get('projectProfiles', []):
                project_completed = self.get_completed_tasks(
                    project['id'],
                    from_time=today.strftime("%Y-%m-%d %H:%M:%S"),
                    to_time=tomorrow.strftime("%Y-%m-%d %H:%M:%S")
                )
                completed_tasks.extend(project_completed)
                
        return {
            'completed': completed_tasks,
            'uncompleted': uncompleted_tasks
        }
    
    def get_this_week_tasks(self, include_completed: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取本周的任务，按完成状态分组
        
        Args:
            include_completed: 是否包含已完成的任务
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的任务
        """
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        next_monday = monday + timedelta(days=7)
        
        # 获取所有未完成任务
        uncompleted_tasks = self.get_all_tasks()
        
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
            task_date = datetime.strptime(task.get('startDate', task.get('dueDate')), "%Y-%m-%dT%H:%M:%S.000+0000") if task.get('startDate') or task.get('dueDate') else None
            if task_date and monday <= task_date < next_monday:
                week_tasks.append(task)
                
        return {
            'completed': completed_tasks,
            'uncompleted': week_tasks
        }
    
    def get_this_month_tasks(self, include_completed: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取本月的任务，按完成状态分组
        
        Args:
            include_completed: 是否包含已完成的任务
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的任务
        """
        today = datetime.now()
        first_day = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
            
        # 获取所有未完成任务
        uncompleted_tasks = self.get_all_tasks()
        
        # 如果需要包含已完成任务，则获取本月完成的任务
        completed_tasks = []
        if include_completed:
            for project in self._get("/api/v2/batch/check/0").get('projectProfiles', []):
                project_completed = self.get_completed_tasks(
                    project['id'],
                    from_time=first_day.strftime("%Y-%m-%d %H:%M:%S"),
                    to_time=next_month.strftime("%Y-%m-%d %H:%M:%S")
                )
                completed_tasks.extend(project_completed)
        
        # 过滤本月的任务
        month_tasks = []
        for task in uncompleted_tasks:
            task_date = datetime.strptime(task.get('startDate', task.get('dueDate')), "%Y-%m-%dT%H:%M:%S.000+0000") if task.get('startDate') or task.get('dueDate') else None
            if task_date and first_day <= task_date < next_month:
                month_tasks.append(task)
                
        return {
            'completed': completed_tasks,
            'uncompleted': month_tasks
        }
    
    def get_next_7_days_tasks(self, include_completed: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取未来7天的任务，按完成状态分组
        
        Args:
            include_completed: 是否包含已完成的任务
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的任务
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        next_week = today + timedelta(days=7)
        
        tasks = self.get_tasks_by_date_range(today, next_week, include_completed)
        return self._group_tasks_by_status(tasks)
    
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有已过期但未完成的任务
        
        Returns:
            List[Dict[str, Any]]: 过期任务列表
        """
        now = datetime.now()
        tasks = self.get_all_tasks()
        overdue_tasks = []
        
        for task in tasks:
            if task.get('status') != 2:  # 未完成
                due_date = datetime.strptime(task.get('dueDate'), "%Y-%m-%dT%H:%M:%S.000+0000") if task.get('dueDate') else None
                if due_date and due_date < now:
                    overdue_tasks.append(task)
                    
        return overdue_tasks
    
    def get_tasks_by_priority(self, priority: int = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取指定优先级的任务，按完成状态分组
        
        Args:
            priority: 优先级 (0-最低, 1-低, 3-中, 5-高)，None表示获取所有优先级
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 按完成状态分组的任务
        """
        tasks = self.get_all_tasks()
        if priority is not None:
            tasks = [task for task in tasks if task.get('priority') == priority]
        return self._group_tasks_by_status(tasks)
    
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
    
    def get_completed_tasks(self, project_id: str, limit: int = 50, from_time: Optional[str] = None, to_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取指定项目中已完成的任务
        
        Args:
            project_id: 项目ID
            limit: 返回的任务数量限制
            from_time: 开始时间，格式为 "2025-02-19 14:44:46"
            to_time: 结束时间，格式为 "2025-02-19 14:44:46"
            
        Returns:
            List[Dict[str, Any]]: 已完成的任务列表
        """
        params = {'limit': limit}
        if from_time:
            params['from'] = from_time
        if to_time:
            params['to'] = to_time
            
        response = self._get(f"/api/v2/project/{project_id}/completed/", params=params)
        
        # 简化数据结构
        return [self._simplify_task_data(task) for task in response] 