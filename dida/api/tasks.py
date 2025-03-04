"""
任务API版本2，支持灵活的任务查询功能
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import pytz
from .base import BaseAPI
from enum import Enum
import random

class ReminderOption(Enum):
    """标准提醒选项"""
    ON_TIME = "0"           # 准时提醒
    BEFORE_5_MIN = "-5M"    # 提前5分钟
    BEFORE_15_MIN = "-15M"  # 提前15分钟
    BEFORE_30_MIN = "-30M"  # 提前30分钟
    BEFORE_1_HOUR = "-1H"   # 提前1小时
    BEFORE_2_HOURS = "-2H"  # 提前2小时
    BEFORE_1_DAY = "-1D"    # 提前1天
    BEFORE_2_DAYS = "-2D"   # 提前2天
    BEFORE_1_WEEK = "-1W"   # 提前1周

    @classmethod
    def get_description(cls, option: str) -> str:
        """获取提醒选项的中文描述"""
        descriptions = {
            cls.ON_TIME.value: "准时提醒",
            cls.BEFORE_5_MIN.value: "提前5分钟",
            cls.BEFORE_15_MIN.value: "提前15分钟",
            cls.BEFORE_30_MIN.value: "提前30分钟",
            cls.BEFORE_1_HOUR.value: "提前1小时",
            cls.BEFORE_2_HOURS.value: "提前2小时",
            cls.BEFORE_1_DAY.value: "提前1天",
            cls.BEFORE_2_DAYS.value: "提前2天",
            cls.BEFORE_1_WEEK.value: "提前1周"
        }
        return descriptions.get(option, "未知提醒类型")

class TaskAPI(BaseAPI):
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

    def get_tasks(self, mode: str = "all", keyword: Optional[str] = None, priority: Optional[int] = None,
                  project_name: Optional[str] = None, tag_names: Optional[List[str]] = None,
                  created_after: Optional[datetime] = None, created_before: Optional[datetime] = None,
                  completed_after: Optional[datetime] = None, completed_before: Optional[datetime] = None,
                  completed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        获取任务，支持多种模式和筛选条件
        
        Args:
            mode: 查询模式，支持 "all", "today", "yesterday", "recent_7_days"
            keyword: 关键词筛选（支持模糊搜索，会搜索标题、内容和子任务）
            priority: 优先级筛选 (0-最低, 1-低, 3-中, 5-高)
            project_name: 项目名称筛选
            tag_names: 标签名称列表筛选
            created_after: 创建时间开始筛选
            created_before: 创建时间结束筛选
            completed_after: 完成时间开始筛选
            completed_before: 完成时间结束筛选
            completed: 是否已完成，True表示已完成，False表示未完成，None表示全部
            
        Returns:
            List[Dict[str, Any]]: 符合条件的任务列表
        """
        tasks = self.get_all_tasks()
        # 如果是查询今天的任务，默认只显示未完成的任务
        if mode == "today" and completed is None:
            completed = False

        def match_keyword(task: Dict[str, Any], kw: str) -> bool:
            """递归检查任务及其子任务是否匹配关键词"""
            # 检查当前任务
            if (kw.lower() in task.get('title', '').lower() or 
                kw.lower() in task.get('content', '').lower()):
                return True
            
            # 递归检查子任务
            for child in task.get('children', []):
                if match_keyword(child, kw):
                    return True
            return False

        def filter_tasks(task_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """递归过滤任务列表"""
            filtered_tasks = []
            for task in task_list:
                # 首先处理子任务
                children = []
                if task.get('children'):
                    children = filter_tasks(task['children'])

                # 检查当前任务是否匹配所有条件
                task_matches = True

                # 首先检查完成状态
                is_completed = self._is_task_completed(task)
                if completed is not None and is_completed != completed:
                    task_matches = False

                # 检查时间相关条件
                if task_matches:
                    if mode == "today" and not self._is_today(task):
                        task_matches = False
                    elif mode == "yesterday" and not self._is_yesterday(task):
                        task_matches = False
                    elif mode == "recent_7_days" and not self._is_recent_7_days(task):
                        task_matches = False

                # 其他过滤条件
                if task_matches:
                    if keyword and not match_keyword(task, keyword):
                        task_matches = False
                    if priority is not None and task.get('priority') != priority:
                        task_matches = False
                    if project_name and project_name.lower() not in task.get('projectName', '').lower():
                        task_matches = False
                    if tag_names and not any(tag in task.get('tags', []) for tag in tag_names):
                        task_matches = False
                    if created_after and self._parse_date(task.get('createdTime')) < created_after:
                        task_matches = False
                    if created_before and self._parse_date(task.get('createdTime')) > created_before:
                        task_matches = False
                    if completed_after and self._parse_date(task.get('completedTime')) < completed_after:
                        task_matches = False
                    if completed_before and self._parse_date(task.get('completedTime')) > completed_before:
                        task_matches = False

                # 如果当前任务匹配或者有匹配的子任务，则添加到结果中
                if task_matches or children:
                    task_copy = task.copy()
                    task_copy['children'] = children
                    filtered_tasks.append(task_copy)

            return filtered_tasks

        return filter_tasks(tasks)

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

    def _is_today(self, task: Dict[str, Any]) -> bool:
        """
        判断任务是否是今天的任务
        规则：
        1. 任务的时间范围（startDate到dueDate）与今天有重叠
        2. 对于全天任务，结束时间应该是当天的23:59:59
        3. 时间判断时要考虑时区
        """
        local_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(local_tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # 获取任务的开始和结束时间
        start_date = self._parse_date(task.get('startDate'))
        due_date = self._parse_date(task.get('dueDate'))

        # 如果既没有开始时间也没有结束时间，则不是今天的任务
        if not start_date and not due_date:
            return False

        # 确保时区一致
        if start_date and start_date.tzinfo is None:
            start_date = local_tz.localize(start_date)
        elif start_date:
            start_date = start_date.astimezone(local_tz)

        if due_date and due_date.tzinfo is None:
            due_date = local_tz.localize(due_date)
        elif due_date:
            due_date = due_date.astimezone(local_tz)

        # 对于全天任务，调整结束时间到当天的23:59:59
        if task.get('isAllDay') and due_date:
            due_date = due_date.replace(hour=23, minute=59, second=59)

        # 检查时间范围是否重叠
        if start_date and due_date:
            return start_date < today_end and due_date >= today_start
        elif start_date:
            return start_date < today_end
        else:  # 只有 due_date
            return due_date >= today_start

    def _is_yesterday(self, task: Dict[str, Any]) -> bool:
        """
        判断任务是否是昨天的任务
        规则：
        1. 任务的时间范围（startDate到dueDate）与昨天有重叠
        2. 对于全天任务，结束时间应该是当天的23:59:59
        3. 时间判断时要考虑时区
        """
        local_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(local_tz)
        yesterday_start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = yesterday_start + timedelta(days=1)

        # 获取任务的开始和结束时间
        start_date = self._parse_date(task.get('startDate'))
        due_date = self._parse_date(task.get('dueDate'))

        # 如果既没有开始时间也没有结束时间，则不是昨天的任务
        if not start_date and not due_date:
            return False

        # 确保时区一致
        if start_date and start_date.tzinfo is None:
            start_date = local_tz.localize(start_date)
        elif start_date:
            start_date = start_date.astimezone(local_tz)

        if due_date and due_date.tzinfo is None:
            due_date = local_tz.localize(due_date)
        elif due_date:
            due_date = due_date.astimezone(local_tz)

        # 对于全天任务，调整结束时间到当天的23:59:59
        if task.get('isAllDay') and due_date:
            due_date = due_date.replace(hour=23, minute=59, second=59)

        # 检查时间范围是否重叠
        if start_date and due_date:
            return start_date < yesterday_end and due_date >= yesterday_start
        elif start_date:
            return start_date < yesterday_end
        else:  # 只有 due_date
            return due_date >= yesterday_start

    def _is_recent_7_days(self, task: Dict[str, Any]) -> bool:
        """
        判断任务是否在最近7天内
        规则：
        1. 任务的时间范围（startDate到dueDate）与未来7天有重叠
        2. 对于全天任务，结束时间应该是当天的23:59:59
        3. 时间判断时要考虑时区
        """
        local_tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(local_tz)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = today_start + timedelta(days=7)

        # 获取任务的开始和结束时间
        start_date = self._parse_date(task.get('startDate'))
        due_date = self._parse_date(task.get('dueDate'))

        # 如果既没有开始时间也没有结束时间，则不在最近7天内
        if not start_date and not due_date:
            return False

        # 确保时区一致
        if start_date and start_date.tzinfo is None:
            start_date = local_tz.localize(start_date)
        elif start_date:
            start_date = start_date.astimezone(local_tz)

        if due_date and due_date.tzinfo is None:
            due_date = local_tz.localize(due_date)
        elif due_date:
            due_date = due_date.astimezone(local_tz)

        # 对于全天任务，调整结束时间到当天的23:59:59
        if task.get('isAllDay') and due_date:
            due_date = due_date.replace(hour=23, minute=59, second=59)

        # 检查时间范围是否重叠
        if start_date and due_date:
            return start_date < week_end and due_date >= today_start
        elif start_date:
            return start_date < week_end
        else:  # 只有 due_date
            return due_date >= today_start

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
        def format_date(date_str: Optional[str]) -> Optional[str]:
            """内部函数：格式化日期字符串"""
            if not date_str:
                return None
            try:
                # 如果包含T和时区信息
                if 'T' in date_str and ('+0000' in date_str or 'Z' in date_str):
                    # 去掉毫秒和时区信息
                    base_time = date_str.split('.')[0]
                    # 解析UTC时间
                    dt = datetime.strptime(base_time, "%Y-%m-%dT%H:%M:%S")
                    # 加8小时转换为北京时间
                    dt = dt + timedelta(hours=8)
                    # 返回简单的时间格式
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                return date_str
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

    def build_task_tree(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将任务列表转换为树形结构
        
        Args:
            tasks: 任务列表
            
        Returns:
            List[Dict[str, Any]]: 树形结构的任务列表
        """
        task_map = {task['id']: task for task in tasks}
        
        for task in tasks:
            task['children'] = []
        
        root_tasks = []
        for task in tasks:
            parent_id = task.get('parentId')
            if parent_id and parent_id in task_map:
                task_map[parent_id]['children'].append(task)
            else:
                root_tasks.append(task)
        
        return root_tasks

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

        if task.get('isCompleted'):
            return True

        return False

    def get_all_tasks(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        tasks = self._get_all_tasks_flat(filters)
        return self.build_task_tree(tasks)

    def _get_all_tasks_flat(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # 获取基本数据
        response = self._get("/api/v2/batch/check/0")
        tasks = []
        
        # 从batch/0获取未完成的任务（只要TEXT类型的）
        for task in response.get('syncTaskBean', {}).get('update', []):
            if task.get('kind') == 'TEXT':
                task['isCompleted'] = False  # 标记为未完成
                tasks.append(task)
        
        # 获取所有项目的已完成任务
        projects = response.get('projectProfiles', [])
        for project in projects:
            completed_tasks = self._get(f"/api/v2/project/{project['id']}/completed/")
            for task in completed_tasks:
                if task.get('kind') == 'TEXT':
                    task['isCompleted'] = True  # 标记为已完成
                    tasks.append(task)

        # 处理所有任务（添加项目和标签信息）
        all_tasks = []
        for task in tasks:
            if task.get('kind') == 'TEXT':
                task = self._merge_project_info(task, projects)
                task = self._merge_tag_info(task, response.get('tags', []))
                simplified_task = self._simplify_task_data(task)
                all_tasks.append(simplified_task)

        # 应用过滤器
        if filters:
            filtered_tasks = []
            for task in all_tasks:
                if self._apply_filters(task, filters):
                    filtered_tasks.append(task)
            return filtered_tasks
        return all_tasks

    def _convert_reminder_format(self, reminder: str) -> str:
        """
        转换简化的提醒格式为API所需的格式
        
        Args:
            reminder: 简化的提醒格式 (如 "0", "-5M", "-1H", "-1D")
            
        Returns:
            str: API格式的提醒字符串
        """
        if not reminder:
            return "TRIGGER:PT0S"
        
        # 如果已经是完整格式，直接返回
        if reminder.startswith("TRIGGER:"):
            return reminder
        
        # 处理准时提醒
        if reminder == "0":
            return "TRIGGER:PT0S"
        
        # 处理其他情况
        if reminder.startswith("-"):
            value = reminder[1:]  # 去掉负号
            unit = value[-1].upper()  # 获取单位（M/H/D/W）
            number = value[:-1]  # 获取数字部分
            
            # 转换周为天
            if unit == "W":
                number = str(int(number) * 7)
                unit = "D"
            
            # 构建API格式
            if unit == "D":
                return f"TRIGGER:-P{number}D"
            else:
                return f"TRIGGER:-PT{number}{unit}"
        
        # 如果格式不正确，返回准时提醒
        return "TRIGGER:PT0S"

    def _generate_reminder_id(self) -> str:
        """
        生成提醒ID，格式类似: 67c5c01e6f3a314670cbebb6
        
        Returns:
            str: 生成的提醒ID
        """
        # 使用当前时间戳的十六进制表示作为基础
        timestamp_hex = hex(int(datetime.now().timestamp()))[2:]
        
        # 生成一个6位的随机十六进制数
        random_hex = hex(random.randint(0, 16777215))[2:].zfill(6)
        
        # 组合ID，确保总长度为24个字符
        reminder_id = f"{timestamp_hex}6f3a{random_hex}"
        
        # 如果长度不足24，用随机字符补齐
        while len(reminder_id) < 24:
            reminder_id += hex(random.randint(0, 15))[2:]
        
        return reminder_id[:24]

    def create_task(self, title: str, content: Optional[str] = None, priority: Optional[int] = None,
                  project_name: Optional[str] = None, tag_names: Optional[List[str]] = None,
                  start_date: Optional[str] = None, due_date: Optional[str] = None,
                  is_all_day: bool = False, reminder: Optional[Union[str, ReminderOption]] = None,
                  parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        创建新任务
        
        Args:
            title: 任务标题
            content: 任务内容
            priority: 优先级 (0-最低, 1-低, 3-中, 5-高)
            project_name: 项目名称
            tag_names: 标签名称列表
            start_date: 开始时间 (格式: YY-MM-DD HH:MM:SS)
            due_date: 到期时间 (格式: YY-MM-DD HH:MM:SS)
            is_all_day: 是否为全天任务
            reminder: 提醒时间，支持以下格式：
                     - "0": 准时提醒
                     - "-5M": 提前5分钟
                     - "-1H": 提前1小时
                     - "-1D": 提前1天
                     - "-1W": 提前1周
                     也可以使用 ReminderOption 枚举值
            parent_id: 父任务ID（如果是子任务）
            
        Returns:
            Dict[str, Any]: 创建的任务数据
        """
        # 获取项目列表
        response = self._get("/api/v2/batch/check/0")
        projects = response.get('projectProfiles', [])
        
        # 构建基本任务数据
        task_data = {
            'title': title,
            'content': content or '',
            'priority': priority or 0,
            'status': 0,
            'kind': 'TEXT',
            'isAllDay': is_all_day,
        }
        
        # 处理项目信息
        if project_name:
            for project in projects:
                if project['name'] == project_name:
                    task_data['projectId'] = project['id']
                    break
        
        # 处理标签
        if tag_names:
            task_data['tags'] = tag_names
        
        # 处理提醒
        if reminder:
            # 如果是枚举值，获取其值
            if isinstance(reminder, ReminderOption):
                reminder_value = reminder.value
            else:
                reminder_value = reminder
            
            # 转换为API格式
            reminder_trigger = self._convert_reminder_format(reminder_value)
            
            # 生成提醒ID
            reminder_id = self._generate_reminder_id()
            
            # 设置提醒
            task_data['reminder'] = reminder_trigger
            task_data['reminders'] = [{
                'id': reminder_id,
                'trigger': reminder_trigger
            }]
        else:
            # 如果没有提醒，设置为空列表
            task_data['reminders'] = []
        
        # 如果是子任务，添加父任务ID
        if parent_id:
            task_data['parentId'] = parent_id
        
        # 处理时间相关字段
        if start_date:
            task_data['startDate'] = self._convert_date_format(date_str=start_date)
        if due_date:
            task_data['dueDate'] = self._convert_date_format(date_str=due_date)
        
        # 设置时区
        task_data['timeZone'] = 'Asia/Shanghai'
        task_data['isFloating'] = False
        
        # 发送创建任务请求
        response = self._post("/api/v2/task", data=task_data)
        
        # 简化并返回创建的任务数据
        return self._simplify_task_data(response)

    def _find_tasks_by_title(self, title: str) -> List[Dict[str, Any]]:
        """
        通过标题模糊匹配查找任务
        
        Args:
            title: 任务标题（支持模糊匹配）
            
        Returns:
            List[Dict[str, Any]]: 匹配的任务列表
        """
        all_tasks = self.get_all_tasks()
        matched_tasks = []
        
        def search_tasks(tasks: List[Dict[str, Any]]):
            for task in tasks:
                if title.lower() in task['title'].lower():
                    matched_tasks.append(task)
                if task.get('children'):
                    search_tasks(task['children'])
        
        search_tasks(all_tasks)
        return matched_tasks

    def update_task(self, task_id_or_title: str, title: Optional[str] = None, content: Optional[str] = None,
                   priority: Optional[int] = None, project_name: Optional[str] = None,
                   tag_names: Optional[List[str]] = None, start_date: Optional[str] = None,
                   due_date: Optional[str] = None, is_all_day: Optional[bool] = None,
                   reminder: Optional[Union[str, ReminderOption]] = None, status: Optional[int] = None) -> Dict[str, Any]:
        """
        更新任务，支持通过ID或标题（模糊匹配）更新
        
        Args:
            task_id_or_title: 任务ID或标题
            title: 新的任务标题
            content: 新的任务内容
            priority: 新的优先级
            project_name: 新的项目名称
            tag_names: 新的标签列表
            start_date: 新的开始时间 (格式: YY-MM-DD HH:MM:SS)
            due_date: 新的到期时间 (格式: YY-MM-DD HH:MM:SS)
            is_all_day: 是否为全天任务
            reminder: 新的提醒时间，支持以下格式：
                     - "0": 准时提醒
                     - "-5M": 提前5分钟
                     - "-1H": 提前1小时
                     - "-1D": 提前1天
                     - "-1W": 提前1周
                     也可以使用 ReminderOption 枚举值
            status: 新的任务状态
            
        Returns:
            Dict[str, Any]: 更新后的任务数据或错误信息
        """
        # 尝试直接通过ID获取任务
        task = self.get_task(task_id_or_title)
        
        # 如果通过ID未找到任务，尝试通过标题模糊匹配
        if not task:
            matched_tasks = self._find_tasks_by_title(task_id_or_title)
            
            if not matched_tasks:
                return {
                    "success": False,
                    "info": f"未找到标题包含 '{task_id_or_title}' 的任务",
                    "data": []
                }
            
            if len(matched_tasks) > 1:
                return {
                    "success": False,
                    "info": f"找到多个标题包含 '{task_id_or_title}' 的任务，请使用更精确的标题或任务ID",
                    "data": matched_tasks
                }
            
            task = matched_tasks[0]
        
        # 构建更新数据
        update_data = task.copy()
        
        if title is not None:
            update_data['title'] = title
        if content is not None:
            update_data['content'] = content
        if priority is not None:
            update_data['priority'] = priority
        if status is not None:
            update_data['status'] = status
        
        # 处理项目信息
        if project_name is not None:
            response = self._get("/api/v2/batch/check/0")
            projects = response.get('projectProfiles', [])
            for project in projects:
                if project['name'] == project_name:
                    update_data['projectId'] = project['id']
                    break
        
        # 处理标签
        if tag_names is not None:
            update_data['tags'] = tag_names
        
        # 处理时间
        if start_date is not None:
            update_data['startDate'] = self._convert_date_format(date_str=start_date)
        
        if due_date is not None:
            update_data['dueDate'] = self._convert_date_format(date_str=due_date)
            if is_all_day or (is_all_day is None and task.get('isAllDay')):
                # 如果是全天任务，确保结束时间是23:59:59
                dt = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(hour=23, minute=59, second=59)
                update_data['dueDate'] = self._convert_date_format(date_obj=dt)
        
        if is_all_day is not None:
            update_data['isAllDay'] = is_all_day
        
        # 处理提醒
        if reminder is not None:
            if reminder:
                # 如果是枚举值，获取其值
                if isinstance(reminder, ReminderOption):
                    reminder_value = reminder.value
                else:
                    reminder_value = reminder
                    
                # 转换为API格式
                reminder_trigger = self._convert_reminder_format(reminder_value)
                
                # 生成提醒ID
                reminder_id = self._generate_reminder_id()
                
                # 设置提醒
                update_data['reminder'] = reminder_trigger
                update_data['reminders'] = [{
                    'id': reminder_id,
                    'trigger': reminder_trigger
                }]
            else:
                # 如果reminder为None，清除提醒
                update_data['reminder'] = None
                update_data['reminders'] = []
        
        try:
            # 发送更新请求
            response = self._post(f"/api/v2/task/{task['id']}", data=update_data)
            return {
                "success": True,
                "info": "任务更新成功",
                "data": self._simplify_task_data(response)
            }
        except Exception as e:
            return {
                "success": False,
                "info": f"更新任务失败: {str(e)}",
                "data": None
            }

    def delete_task(self, task_id_or_title: str) -> Dict[str, Any]:
        """
        删除任务，支持通过ID或标题（模糊匹配）删除
        
        Args:
            task_id_or_title: 任务ID或标题
            
        Returns:
            Dict[str, Any]: 删除操作的结果
        """
        # 尝试直接通过ID获取任务
        task = self.get_task(task_id_or_title)
        
        # 如果通过ID未找到任务，尝试通过标题模糊匹配
        if not task:
            matched_tasks = self._find_tasks_by_title(task_id_or_title)
            
            # 如果没有找到匹配的任务
            if not matched_tasks:
                return {
                    "success": False,
                    "info": f"未找到标题包含 '{task_id_or_title}' 的任务",
                    "data": []
                }
            
            # 如果找到多个匹配的任务
            if len(matched_tasks) > 1:
                return {
                    "success": False,
                    "info": f"找到多个标题包含 '{task_id_or_title}' 的任务，请使用更精确的标题或任务ID",
                    "data": matched_tasks
                }
            
            # 如果只找到一个匹配的任务
            task = matched_tasks[0]
        
        try:
            # 准备删除任务的数据
            delete_data = {
                "delete": [
                    {
                        "taskId": task['id'],
                        "projectId": task['projectId']
                    }
                ]
            }
            
            # 发送批量删除请求
            self._post("/api/v2/batch/task", data=delete_data)
            
            return {
                "success": True,
                "info": f"成功删除任务 '{task['title']}'",
                "data": task
            }
        except Exception as e:
            return {
                "success": False,
                "info": f"删除任务失败: {str(e)}",
                "data": task
            }

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个任务的详细信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Dict[str, Any]]: 任务数据，如果任务不存在则返回None
        """
        try:
            response = self._get(f"/api/v2/task/{task_id}")
            return self._simplify_task_data(response)
        except Exception:
            return None 