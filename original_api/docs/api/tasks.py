import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import requests
from dataclasses import dataclass
import json

class DidaTaskProcessor:
    """滴答清单任务数据处理器"""
    
    @staticmethod
    def get_token(email: str, password: str) -> str:
        """
        获取滴答清单的访问令牌
        
        Args:
            email: 用户邮箱
            password: 用户密码
            
        Returns:
            str: 访问令牌
            
        Raises:
            Exception: 当登录失败时
        """
        login_url = "https://dida365.com/api/v2/user/signon?wc=true&remember=true"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        payload = {
            "username": email,
            "password": password
        }
        
        try:
            response = requests.post(login_url, json=payload, headers=headers)
            response.raise_for_status()
            token = response.cookies.get("t")
            if not token:
                raise Exception("登录成功但未获取到token")
            return token
        except requests.exceptions.RequestException as e:
            raise Exception(f"登录失败: {str(e)}")
    
    def __init__(self, token: str = None, email: str = None, password: str = None):
        """
        初始化处理器
        
        Args:
            token: 认证token
            email: 用户邮箱（如果没有提供token）
            password: 用户密码（如果没有提供token）
        """
        if token is None and (email is not None and password is not None):
            token = self.get_token(email, password)
        elif token is None:
            raise ValueError("必须提供token或者email和password")
            
        self.token = token
        self.headers = {
            "Cookie": f"t={token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.tasks_df = None
        self.projects_df = None
        self.project_groups_df = None
        self.tags_df = None
        
    def get_all_data(self, checkpoint: int = 0) -> Dict:
        """获取所有同步数据"""
        url = f"https://api.dida365.com/api/v2/batch/check/{checkpoint}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取数据失败: {str(e)}")
    
    def process_tasks(self, tasks_data: List[Dict]) -> pd.DataFrame:
        """处理任务数据为DataFrame"""
        # 展开任务数据，处理嵌套字段
        tasks = []
        for task in tasks_data:
            task_dict = task.copy()
            
            # 处理标签列表
            task_dict['tag_names'] = ','.join(task.get('tags', []))
            
            # 处理附件
            if 'attachments' in task:
                task_dict['attachment_count'] = len(task['attachments'])
                task_dict['attachment_ids'] = ','.join([att['id'] for att in task['attachments']])
            else:
                task_dict['attachment_count'] = 0
                task_dict['attachment_ids'] = ''
            
            # 处理提醒时间
            task_dict['reminder_times'] = ','.join([str(r) for r in task.get('reminders', [])])
            
            # 处理子任务
            task_dict['subtask_count'] = len(task.get('items', []))
            
            tasks.append(task_dict)
        
        return pd.DataFrame(tasks)
    
    def process_projects(self, projects_data: List[Dict]) -> pd.DataFrame:
        """处理项目数据为DataFrame"""
        return pd.DataFrame(projects_data)
    
    def process_project_groups(self, groups_data: List[Dict]) -> pd.DataFrame:
        """处理项目组数据为DataFrame"""
        return pd.DataFrame(groups_data)
    
    def process_tags(self, tags_data: List[Dict]) -> pd.DataFrame:
        """处理标签数据为DataFrame"""
        return pd.DataFrame(tags_data)
    
    def create_wide_table(self, data: Dict) -> pd.DataFrame:
        """
        创建包含所有关联信息的宽表
        
        Args:
            data: 原始同步数据
            
        Returns:
            pd.DataFrame: 包含所有关联信息的宽表
        """
        # 处理各个数据源
        self.tasks_df = self.process_tasks(data.get('syncTaskBean', {}).get('update', []))
        self.projects_df = self.process_projects(data.get('projectProfiles', []))
        self.project_groups_df = self.process_project_groups(data.get('projectGroups', []))
        self.tags_df = self.process_tags(data.get('tags', []))
        
        # 开始关联
        # 1. 任务与项目关联
        if not self.tasks_df.empty and not self.projects_df.empty:
            wide_df = self.tasks_df.merge(
                self.projects_df,
                left_on='projectId',
                right_on='id',
                how='left',
                suffixes=('', '_project')
            )
        else:
            wide_df = self.tasks_df
            
        # 2. 项目与项目组关联
        if not self.project_groups_df.empty:
            wide_df = wide_df.merge(
                self.project_groups_df,
                left_on='groupId',
                right_on='id',
                how='left',
                suffixes=('', '_group')
            )
            
        # 3. 处理标签关联（通过tag_names字段）
        if not self.tags_df.empty:
            # 创建标签映射
            tag_info = {
                tag['name']: {
                    'tag_color': tag['color'],
                    'tag_sort_order': tag['sortOrder']
                }
                for _, tag in self.tags_df.iterrows()
            }
            
            # 添加标签相关列
            wide_df['tag_colors'] = wide_df['tag_names'].apply(
                lambda x: ','.join([tag_info.get(tag, {}).get('tag_color', '') 
                                  for tag in (x.split(',') if x else [])])
            )
            wide_df['tag_sort_orders'] = wide_df['tag_names'].apply(
                lambda x: ','.join([str(tag_info.get(tag, {}).get('tag_sort_order', '')) 
                                  for tag in (x.split(',') if x else [])])
            )
        
        return wide_df
    
    def query_tasks(self, wide_df: pd.DataFrame, **filters) -> pd.DataFrame:
        """
        根据条件查询任务
        
        Args:
            wide_df: 宽表数据
            **filters: 过滤条件，支持：
                - project_name: 项目名称
                - tag_names: 标签名称列表
                - priority: 优先级
                - status: 任务状态
                - due_date_start: 截止日期开始
                - due_date_end: 截止日期结束
                
        Returns:
            pd.DataFrame: 过滤后的任务数据
        """
        query_df = wide_df.copy()
        
        if 'project_name' in filters:
            query_df = query_df[query_df['name'] == filters['project_name']]
            
        if 'tag_names' in filters:
            tags = filters['tag_names']
            if isinstance(tags, str):
                tags = [tags]
            query_df = query_df[query_df['tag_names'].apply(
                lambda x: any(tag in (x.split(',') if x else []) for tag in tags)
            )]
            
        if 'priority' in filters:
            query_df = query_df[query_df['priority'] == filters['priority']]
            
        if 'status' in filters:
            query_df = query_df[query_df['status'] == filters['status']]
            
        if 'due_date_start' in filters:
            query_df = query_df[query_df['dueDate'] >= filters['due_date_start']]
            
        if 'due_date_end' in filters:
            query_df = query_df[query_df['dueDate'] <= filters['due_date_end']]
        
        return query_df

    def analyze_table_structure(self, wide_df: pd.DataFrame) -> None:
        """
        分析并打印宽表结构
        
        Args:
            wide_df: 宽表数据
        """
        print("\n=== 滴答清单任务宽表结构分析 ===")
        
        # 1. 基本信息
        print(f"\n1. 基本信息:")
        print(f"总行数: {len(wide_df)}")
        print(f"总列数: {len(wide_df.columns)}")
        
        # 2. 列信息
        print(f"\n2. 列信息:")
        print("\n字段名称 | 数据类型 | 非空值数量 | 示例值")
        print("-" * 60)
        for col in wide_df.columns:
            non_null = wide_df[col].count()
            example = wide_df[col].iloc[0] if non_null > 0 else None
            if isinstance(example, str) and len(example) > 30:
                example = example[:30] + "..."
            print(f"{col} | {wide_df[col].dtype} | {non_null} | {example}")
        
        # 3. 任务统计
        print(f"\n3. 任务统计:")
        if 'status' in wide_df.columns:
            status_counts = wide_df['status'].value_counts()
            print("\n任务状态分布:")
            for status, count in status_counts.items():
                status_name = "完成" if status == 2 else "未完成" if status == 0 else "其他"
                print(f"- {status_name}: {count}个")
        
        if 'priority' in wide_df.columns:
            priority_counts = wide_df['priority'].value_counts()
            print("\n优先级分布:")
            for priority, count in priority_counts.items():
                print(f"- 优先级{priority}: {count}个")
        
        # 4. 项目统计
        if 'name' in wide_df.columns:  # 项目名称
            project_counts = wide_df['name'].value_counts()
            print("\n项目分布:")
            for project, count in project_counts.head().items():
                print(f"- {project}: {count}个任务")
        
        # 5. 标签统计
        if 'tag_names' in wide_df.columns:
            all_tags = []
            for tags in wide_df['tag_names'].dropna():
                if tags:
                    all_tags.extend(tags.split(','))
            tag_counts = pd.Series(all_tags).value_counts()
            print("\n标签使用情况:")
            for tag, count in tag_counts.head().items():
                print(f"- {tag}: {count}次使用")

    def batch_tasks(self, add_tasks: List[Dict] = None, update_tasks: List[Dict] = None, 
                   delete_tasks: List[Dict] = None, add_attachments: List[Dict] = None,
                   update_attachments: List[Dict] = None, delete_attachments: List[Dict] = None) -> Dict:
        """
        批量处理任务（增删改）及其附件
        
        Args:
            add_tasks: 需要添加的任务列表
            update_tasks: 需要更新的任务列表
            delete_tasks: 需要删除的任务列表
            add_attachments: 需要添加的附件列表
            update_attachments: 需要更新的附件列表
            delete_attachments: 需要删除的附件列表
            
        Returns:
            Dict: API响应结果
            
        Raises:
            Exception: 当API请求失败时
        """
        url = "https://api.dida365.com/api/v2/batch/task"
        
        payload = {
            "add": add_tasks or [],
            "update": update_tasks or [],
            "delete": delete_tasks or [],
            "addAttachments": add_attachments or [],
            "updateAttachments": update_attachments or [],
            "deleteAttachments": delete_attachments or []
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"批量处理任务失败: {str(e)}")

    def get_project_id_by_name(self, project_name: str) -> Optional[str]:
        """
        通过项目名称获取项目ID
        
        Args:
            project_name: 项目名称
            
        Returns:
            str: 项目ID，如果未找到则返回None
        """
        data = self.get_all_data()
        projects = data.get('projectProfiles', [])
        
        for project in projects:
            if project.get('name') == project_name:
                return project.get('id')
        return None

    def add_task(self, title: str, **kwargs) -> Dict:
        """
        添加任务
        
        Args:
            title: 任务标题（必填）
            **kwargs: 可选参数，支持以下字段：
                - content: str, 任务描述
                - project_name: str, 项目名称（会自动转换为projectId）
                - projectId: str, 项目ID（如果提供了project_name则不需要）
                - status: int, 任务状态 (0:待办, 2:已完成)
                - priority: int, 优先级 (1-5，值越大优先级越高)
                - startDate: str, 开始时间 (ISO 8601格式)
                - dueDate: str, 截止时间 (ISO 8601格式)
                - isAllDay: bool, 是否全天任务
                - tags: List[str], 标签列表
                - items: List[Dict], 子任务列表
                - reminders: List[str], 提醒时间列表 (ISO 8601格式)
                
        Returns:
            Dict: 创建的任务数据
        """
        url = "https://api.dida365.com/api/v2/task"
        
        # 准备任务数据
        task_data = {"title": title}
        
        # 处理项目名称
        if 'project_name' in kwargs:
            project_id = self.get_project_id_by_name(kwargs.pop('project_name'))
            if not project_id:
                raise ValueError(f"项目 '{kwargs['project_name']}' 不存在")
            task_data['projectId'] = project_id
            
        task_data.update(kwargs)
        
        try:
            response = requests.post(url, json=task_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"创建任务失败: {str(e)}")

    def update_task(self, task_id: str, **kwargs) -> Dict:
        """
        更新任务
        
        Args:
            task_id: 任务ID（必填）
            **kwargs: 要更新的字段，支持以下常用操作：
                - title: str, 任务标题
                - content: str, 任务描述
                - project_name: str, 项目名称（会自动转换为projectId）
                - projectId: str, 项目ID（如果提供了project_name则不需要）
                - status: int, 任务状态 (0:待办, 2:已完成)
                - priority: int, 优先级 (1-5)
                - startDate: str, 开始时间
                - dueDate: str, 截止时间
                - tags: List[str], 标签列表
                - add_tags: List[str], 要添加的标签列表
                - remove_tags: List[str], 要移除的标签列表
                
        Returns:
            Dict: 更新后的任务数据
        """
        url = f"https://api.dida365.com/api/v2/task/{task_id}"
        
        try:
            # 先获取当前任务数据
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            task_data = response.json()
            
            # 处理项目名称
            if 'project_name' in kwargs:
                project_id = self.get_project_id_by_name(kwargs.pop('project_name'))
                if not project_id:
                    raise ValueError(f"项目 '{kwargs['project_name']}' 不存在")
                kwargs['projectId'] = project_id
            
            # 处理标签操作
            if 'add_tags' in kwargs:
                current_tags = set(task_data.get('tags', []))
                current_tags.update(kwargs.pop('add_tags'))
                kwargs['tags'] = list(current_tags)
                
            if 'remove_tags' in kwargs:
                current_tags = set(task_data.get('tags', []))
                current_tags.difference_update(kwargs.pop('remove_tags'))
                kwargs['tags'] = list(current_tags)
            
            # 更新指定字段
            task_data.update(kwargs)
            
            # 发送更新请求
            response = requests.put(url, json=task_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"更新任务失败: {str(e)}")

    def delete_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        url = f"https://api.dida365.com/api/v2/task/{task_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"删除任务失败: {str(e)}")

    def complete_task(self, task_id: str) -> Dict:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 更新后的任务数据
        """
        return self.update_task(task_id, status=2)

    def add_tasks(self, tasks_data: List[Dict]) -> Dict:
        """
        批量添加任务
        
        Args:
            tasks_data: 任务数据列表，每个任务必须包含title和projectId
            
        Returns:
            Dict: API响应结果
            
        Raises:
            Exception: 当创建失败时
        """
        for task in tasks_data:
            required_fields = ['title', 'projectId']
            for field in required_fields:
                if field not in task:
                    raise ValueError(f"任务数据缺少必填字段: {field}")
                    
        return self.batch_tasks(add_tasks=tasks_data)

    def update_tasks(self, tasks_data: List[Dict]) -> Dict:
        """
        批量更新任务
        
        Args:
            tasks_data: 任务数据列表，每个任务必须包含id和projectId
            
        Returns:
            Dict: API响应结果
            
        Raises:
            Exception: 当更新失败时
        """
        for task in tasks_data:
            required_fields = ['id', 'projectId']
            for field in required_fields:
                if field not in task:
                    raise ValueError(f"任务数据缺少必填字段: {field}")
                    
        return self.batch_tasks(update_tasks=tasks_data)

    def delete_tasks(self, task_ids: List[str], project_id: str) -> Dict:
        """
        批量删除任务
        
        Args:
            task_ids: 任务ID列表
            project_id: 项目ID
            
        Returns:
            Dict: API响应结果
            
        Raises:
            Exception: 当删除失败时
        """
        delete_data = [
            {"taskId": task_id, "projectId": project_id}
            for task_id in task_ids
        ]
        return self.batch_tasks(delete_tasks=delete_data)

    def complete_tasks(self, task_ids: List[str], project_id: str) -> Dict:
        """
        批量完成任务
        
        Args:
            task_ids: 任务ID列表
            project_id: 项目ID
            
        Returns:
            Dict: API响应结果
            
        Raises:
            Exception: 当更新失败时
        """
        completed_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000+0000")
        update_data = [
            {
                "id": task_id,
                "projectId": project_id,
                "status": 2,  # 2表示已完成
                "completedTime": completed_time
            }
            for task_id in task_ids
        ]
        return self.batch_tasks(update_tasks=update_data)

    def simple_add_task(self, title: str, **kwargs) -> Dict:
        """
        使用简化方式添加任务
        
        Args:
            title: 任务标题（必填）
            **kwargs: 可选参数，支持以下字段：
                - content: str, 任务描述
                - projectId: str, 项目ID
                - status: int, 任务状态 (0:待办, 2:已完成)
                - priority: int, 优先级 (1-5，值越大优先级越高)
                - startDate: str, 开始时间 (ISO 8601格式)
                - dueDate: str, 截止时间 (ISO 8601格式)
                - isAllDay: bool, 是否全天任务
                - tags: List[str], 标签列表
                - items: List[Dict], 子任务列表
                - reminders: List[str], 提醒时间列表 (ISO 8601格式)
                
        Returns:
            Dict: 创建的任务数据
        """
        url = "https://api.dida365.com/api/v2/task"
        
        # 准备任务数据
        task_data = {"title": title}
        task_data.update(kwargs)
        
        try:
            response = requests.post(url, json=task_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"创建任务失败: {str(e)}")

    def simple_update_task(self, task_id: str, **kwargs) -> Dict:
        """
        使用简化方式更新任务
        
        Args:
            task_id: 任务ID（必填）
            **kwargs: 要更新的字段，支持任务的所有字段
                常用字段包括：
                - title: str, 任务标题
                - content: str, 任务描述
                - status: int, 任务状态 (0:待办, 2:已完成)
                - priority: int, 优先级 (1-5)
                - startDate: str, 开始时间
                - dueDate: str, 截止时间
                - tags: List[str], 标签列表
                
        Returns:
            Dict: 更新后的任务数据
        """
        url = f"https://api.dida365.com/api/v2/task/{task_id}"
        
        try:
            # 先获取当前任务数据
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            task_data = response.json()
            
            # 更新指定字段
            task_data.update(kwargs)
            
            # 发送更新请求
            response = requests.put(url, json=task_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"更新任务失败: {str(e)}")

    def simple_delete_task(self, task_id: str) -> bool:
        """
        使用简化方式删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        url = f"https://api.dida365.com/api/v2/task/{task_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise Exception(f"删除任务失败: {str(e)}")

    def simple_complete_task(self, task_id: str) -> Dict:
        """
        使用简化方式完成任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 更新后的任务数据
        """
        return self.simple_update_task(task_id, status=2)

    def simple_batch_add_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        批量添加任务的简化方法
        
        Args:
            tasks: 任务数据列表，每个任务必须包含title字段
                
        Returns:
            List[Dict]: 创建的任务数据列表
        """
        results = []
        for task in tasks:
            if 'title' not in task:
                raise ValueError("每个任务必须包含title字段")
            result = self.simple_add_task(**task)
            results.append(result)
        return results

    def simple_batch_update_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """
        批量更新任务的简化方法
        
        Args:
            tasks: 任务数据列表，每个任务必须包含id字段和要更新的字段
                
        Returns:
            List[Dict]: 更新后的任务数据列表
        """
        results = []
        for task in tasks:
            if 'id' not in task:
                raise ValueError("每个任务必须包含id字段")
            task_id = task.pop('id')
            result = self.simple_update_task(task_id, **task)
            results.append(result)
        return results

    def simple_batch_delete_tasks(self, task_ids: List[str]) -> bool:
        """
        批量删除任务的简化方法
        
        Args:
            task_ids: 任务ID列表
                
        Returns:
            bool: 是否全部删除成功
        """
        success = True
        for task_id in task_ids:
            try:
                self.simple_delete_task(task_id)
            except Exception:
                success = False
        return success

    def simple_batch_complete_tasks(self, task_ids: List[str]) -> List[Dict]:
        """
        批量完成任务的简化方法
        
        Args:
            task_ids: 任务ID列表
                
        Returns:
            List[Dict]: 更新后的任务数据列表
        """
        return self.simple_batch_update_tasks([
            {'id': task_id, 'status': 2}
            for task_id in task_ids
        ])

    def get_tag_info_by_name(self, tag_name: str) -> Optional[Dict]:
        """
        通过标签名称获取标签信息
        
        Args:
            tag_name: 标签名称
            
        Returns:
            Dict: 标签信息，包含id、color等，如果未找到则返回None
        """
        data = self.get_all_data()
        tags = data.get('tags', [])
        
        for tag in tags:
            if tag.get('name') == tag_name:
                return tag
        return None

    def move_task_to_project(self, task_id: str, project_name: str) -> Dict:
        """
        将任务移动到指定名称的项目中
        
        Args:
            task_id: 任务ID
            project_name: 目标项目名称
            
        Returns:
            Dict: 更新后的任务数据
            
        Raises:
            ValueError: 当项目不存在时
        """
        project_id = self.get_project_id_by_name(project_name)
        if not project_id:
            raise ValueError(f"项目 '{project_name}' 不存在")
            
        return self.update_task(task_id, projectId=project_id)

    def add_task_with_project(self, title: str, project_name: str, **kwargs) -> Dict:
        """
        在指定项目中创建任务
        
        Args:
            title: 任务标题
            project_name: 项目名称
            **kwargs: 其他任务参数
            
        Returns:
            Dict: 创建的任务数据
            
        Raises:
            ValueError: 当项目不存在时
        """
        project_id = self.get_project_id_by_name(project_name)
        if not project_id:
            raise ValueError(f"项目 '{project_name}' 不存在")
            
        kwargs['projectId'] = project_id
        return self.add_task(title, **kwargs)

    def add_tags_to_task(self, task_id: str, tag_names: List[str]) -> Dict:
        """
        为任务添加标签
        
        Args:
            task_id: 任务ID
            tag_names: 标签名称列表
            
        Returns:
            Dict: 更新后的任务数据
        """
        # 获取当前任务信息
        url = f"https://api.dida365.com/api/v2/task/{task_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        task_data = response.json()
        
        # 获取现有标签
        current_tags = task_data.get('tags', [])
        
        # 添加新标签
        new_tags = list(set(current_tags + tag_names))
        
        return self.update_task(task_id, tags=new_tags)

    def remove_tags_from_task(self, task_id: str, tag_names: List[str]) -> Dict:
        """
        从任务中移除标签
        
        Args:
            task_id: 任务ID
            tag_names: 要移除的标签名称列表
            
        Returns:
            Dict: 更新后的任务数据
        """
        # 获取当前任务信息
        url = f"https://api.dida365.com/api/v2/task/{task_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        task_data = response.json()
        
        # 获取现有标签
        current_tags = task_data.get('tags', [])
        
        # 移除指定标签
        new_tags = [tag for tag in current_tags if tag not in tag_names]
        
        return self.update_task(task_id, tags=new_tags)

    def set_task_tags(self, task_id: str, tag_names: List[str]) -> Dict:
        """
        设置任务的标签（替换现有标签）
        
        Args:
            task_id: 任务ID
            tag_names: 新的标签名称列表
            
        Returns:
            Dict: 更新后的任务数据
        """
        return self.update_task(task_id, tags=tag_names)

# 使用示例
if __name__ == "__main__":
    # 使用邮箱密码初始化
    processor = DidaTaskProcessor(
        email="your_email@example.com",
        password="your_password"
    )
    
    # 创建任务（直接指定项目名称）
    new_task = processor.add_task(
        title="测试任务",
        project_name="工作",  # 自动转换为projectId
        content="这是一个测试任务",
        priority=3,
        tags=["工作", "重要"]  # 直接设置标签
    )
    
    # 更新任务（移动到其他项目）
    moved_task = processor.update_task(
        new_task['id'],
        project_name="个人"  # 自动转换为projectId
    )
    
    # 更新任务（添加标签）
    task_with_tags = processor.update_task(
        new_task['id'],
        add_tags=["紧急", "会议"]  # 添加新标签
    )
    
    # 更新任务（移除标签）
    task_without_tags = processor.update_task(
        new_task['id'],
        remove_tags=["会议"]  # 移除指定标签
    )
    
    # 更新任务（直接设置标签）
    task_with_new_tags = processor.update_task(
        new_task['id'],
        tags=["个人", "学习"]  # 替换所有标签
    )
    
    # 完成任务
    completed_task = processor.complete_task(new_task['id'])
    
    # 删除任务
    is_deleted = processor.delete_task(new_task['id'])
    
    # 获取数据
    data = processor.get_all_data()
    
    # 创建宽表
    wide_df = processor.create_wide_table(data)
    
    # 分析表结构
    processor.analyze_table_structure(wide_df)
    
    # 保存到Excel文件以便查看完整数据
    # to_excel()方法不支持encoding参数,移除该参数
    wide_df.to_excel('tasks_wide_table.xlsx', index=False)
    print("\n完整数据已保存到 tasks_wide_table.xlsx")
    print(wide_df.head(1))
    
    # # 查询示例
    # # 1. 查询特定项目的任务
    # project_tasks = processor.query_tasks(wide_df, project_name="工作")
    
    # # 2. 查询包含特定标签的任务
    # tagged_tasks = processor.query_tasks(wide_df, tag_names=["重要"])
    
    # # 3. 查询高优先级且未完成的任务
    # important_tasks = processor.query_tasks(
    #     wide_df,
    #     priority=5,
    #     status=0
    # )
    
    # # 4. 查询特定日期范围的任务
    # date_tasks = processor.query_tasks(
    #     wide_df,
    #     due_date_start="2024-02-01",
    #     due_date_end="2024-02-29"
    # ) 