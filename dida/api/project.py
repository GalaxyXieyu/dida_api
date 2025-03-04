"""
项目相关API
"""
from typing import List, Optional, Dict, Any
from .base import BaseAPI
from datetime import datetime
import pytz

class ProjectAPI(BaseAPI):
    """项目相关的API实现"""
    
    def get_projects(self, name: Optional[str] = None, color: Optional[str] = None,
                    group_id: Optional[str] = None, include_tasks: bool = True) -> List[Dict[str, Any]]:
        """
        获取项目列表，支持多种筛选条件
        
        Args:
            name: 项目名称筛选
            color: 项目颜色筛选
            group_id: 项目组ID筛选
            include_tasks: 是否包含任务列表
            
        Returns:
            List[Dict[str, Any]]: 项目列表
        """
        response = self._get("/api/v2/batch/check/0")
        projects_data = response.get('projectProfiles', [])
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        
        # 处理项目数据
        result = []
        for project in projects_data:
            match = True
            
            # 应用筛选条件
            if name and project.get('name') != name:
                match = False
            if color and project.get('color') != color:
                match = False
            if group_id and project.get('groupId') != group_id:
                match = False
            
            if match:
                project_data = project.copy()
                
                # 添加任务列表（如果需要）
                if include_tasks:
                    project_tasks = [
                        task for task in tasks_data
                        if task.get('projectId') == project['id']
                    ]
                    project_data['tasks'] = project_tasks
                    
                result.append(project_data)
                
        return result

    def create_project(self, name: str, color: Optional[str] = None,
                      group_id: Optional[str] = None, view_mode: str = "list",
                      is_inbox: bool = False) -> Dict[str, Any]:
        """
        创建新项目
        
        Args:
            name: 项目名称
            color: 项目颜色
            group_id: 项目组ID
            view_mode: 视图模式，默认为list
            is_inbox: 是否为收集箱
            
        Returns:
            Dict[str, Any]: 创建的项目数据
        """
        project_data = {
            "name": name,
            "color": color,
            "groupId": group_id,
            "viewMode": view_mode,
            "inAll": True,
            "sortOrder": 0,
            "sortType": "sortOrder",
            "isInbox": is_inbox
        }
        
        # 移除None值的字段
        project_data = {k: v for k, v in project_data.items() if v is not None}
        
        response = self._post("/api/v2/project", data=project_data)
        return response

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个项目的详细信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            Optional[Dict[str, Any]]: 项目数据，如果项目不存在则返回None
        """
        try:
            response = self._get(f"/api/v2/project/{project_id}")
            return response
        except Exception:
            return None

    def update_project(self, project_id: str, name: Optional[str] = None,
                      color: Optional[str] = None, group_id: Optional[str] = None,
                      view_mode: Optional[str] = None, sort_order: Optional[int] = None,
                      sort_type: Optional[str] = None, sort_option: Optional[Dict] = None,
                      timeline: Optional[Dict] = None, team_id: Optional[str] = None,
                      permission: Optional[str] = None, kind: Optional[str] = None,
                      need_audit: Optional[bool] = None, barcode_need_audit: Optional[bool] = None,
                      open_to_team: Optional[bool] = None, team_member_permission: Optional[str] = None,
                      notification_options: Optional[List] = None) -> Dict[str, Any]:
        """
        更新项目信息
        
        Args:
            project_id: 项目ID
            name: 项目名称
            color: 项目颜色
            group_id: 项目组ID
            view_mode: 视图模式 (list, kanban等)
            sort_order: 排序顺序
            sort_type: 排序类型
            sort_option: 排序选项
            timeline: 时间线设置
            team_id: 团队ID
            permission: 权限设置
            kind: 项目类型 (TASK, NOTE等)
            need_audit: 是否需要审核
            barcode_need_audit: 条码是否需要审核
            open_to_team: 是否对团队开放
            team_member_permission: 团队成员权限
            notification_options: 通知选项
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        # 获取所有项目信息
        response = self._get("/api/v2/batch/check/0")
        projects = response.get('projectProfiles', [])
        
        # 查找当前项目
        current_project = None
        for project in projects:
            if project['id'] == project_id:
                current_project = project
                break
                
        if not current_project:
            return {
                "success": False,
                "info": f"未找到ID为 '{project_id}' 的项目",
                "data": None
            }
        
        # 构建更新数据，保持原有数据不变
        update_data = current_project.copy()
        
        # 更新提供的字段
        if name is not None:
            update_data['name'] = name
        if color is not None:
            update_data['color'] = color
        if group_id is not None:
            update_data['groupId'] = group_id
        if view_mode is not None:
            update_data['viewMode'] = view_mode
        if sort_order is not None:
            update_data['sortOrder'] = sort_order
        if sort_type is not None:
            update_data['sortType'] = sort_type
        if sort_option is not None:
            update_data['sortOption'] = sort_option
        if timeline is not None:
            update_data['timeline'] = timeline
        if team_id is not None:
            update_data['teamId'] = team_id
        if permission is not None:
            update_data['permission'] = permission
        if kind is not None:
            update_data['kind'] = kind
        if need_audit is not None:
            update_data['needAudit'] = need_audit
        if barcode_need_audit is not None:
            update_data['barcodeNeedAudit'] = barcode_need_audit
        if open_to_team is not None:
            update_data['openToTeam'] = open_to_team
        if team_member_permission is not None:
            update_data['teamMemberPermission'] = team_member_permission
        if notification_options is not None:
            update_data['notificationOptions'] = notification_options

        # 构建批量更新格式
        batch_data = {
            "add": [],
            "update": [update_data],
            "delete": []
        }

        try:
            # 发送批量更新请求
            response = self._post("/api/v2/batch/project", data=batch_data)
            return {
                "success": True,
                "info": "项目更新成功",
                "data": response
            }
        except Exception as e:
            return {
                "success": False,
                "info": f"更新项目失败: {str(e)}",
                "data": None
            }

    def delete_project(self, project_id: str) -> Dict[str, Any]:
        """
        删除项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            Dict[str, Any]: 删除操作的结果
        """
        try:
            # 获取所有项目信息
            response = self._get("/api/v2/batch/check/0")
            projects = response.get('projectProfiles', [])
            
            # 查找当前项目
            current_project = None
            for project in projects:
                if project['id'] == project_id:
                    current_project = project
                    break
                    
            if not current_project:
                return {
                    "success": False,
                    "info": f"未找到ID为 '{project_id}' 的项目",
                    "data": None
                }
            
            # 构建批量删除格式
            batch_data = {
                "add": [],
                "update": [],
                "delete": [project_id]
            }
            
            # 发送批量删除请求
            response = self._post("/api/v2/batch/project", data=batch_data)
            
            return {
                "success": True,
                "info": f"成功删除项目 '{current_project.get('name', project_id)}'",
                "data": response
            }
        except Exception as e:
            return {
                "success": False,
                "info": f"删除项目失败: {str(e)}",
                "data": None
            }

    def get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """
        获取项目下的所有任务
        
        Args:
            project_id: 项目ID
            
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        response = self._get("/api/v2/batch/check/0")
        tasks_data = response.get('syncTaskBean', {}).get('update', [])
        return [
            task for task in tasks_data
            if task.get('projectId') == project_id
        ] 