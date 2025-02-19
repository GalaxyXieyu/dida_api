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
    
    def _is_task_completed(self, task: Dict[str, Any]) -> bool:
        """
        判断任务是否已完成
        
        Args:
            task: 任务数据
            
        Returns:
            bool: 是否已完成
        """
        column_id = task.get('columnId')
        if not column_id:
            return False
            
        # 如果是已完成栏目
        if column_id in self._completed_columns:
            return True
            
        # 如果有栏目信息，检查栏目名称
        if column_id in self._column_info:
            column = self._column_info[column_id]
            return '已完成' in column.get('name', '')
            
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
        response = self._get("/api/v2/batch/check/0")
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        projects = response.get('projectProfiles', [])
        tags = response.get('tags', [])
        
        # 更新栏目信息
        self._update_column_info(projects)
        
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
        
        tasks = self.get_tasks_by_date_range(today, tomorrow, include_completed)
        return self._group_tasks_by_status(tasks)
    
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
        
        tasks = self.get_tasks_by_date_range(monday, next_monday, include_completed)
        return self._group_tasks_by_status(tasks)
    
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
            
        tasks = self.get_tasks_by_date_range(first_day, next_month, include_completed)
        return self._group_tasks_by_status(tasks)
    
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
        all_tasks = self.get_all_tasks()
        completed_tasks = [task for task in all_tasks if self._is_task_completed(task)]
        uncompleted_tasks = [task for task in all_tasks if not self._is_task_completed(task)]
        overdue_tasks = self.get_overdue_tasks()
        
        # 按优先级统计
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