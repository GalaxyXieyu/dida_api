# 项目管理接口

## 获取项目列表

### 基本信息
- 接口名称：获取项目列表
- 接口描述：获取用户的所有项目列表
- 请求方法：GET
- 请求URL：/project/all
- 请求参数格式：无

### 响应数据结构
```json
[
    {
        "id": "ef68424f99ef959ef1218e4e",
        "name": "工作",
        "color": "#FF6161",
        "sortOrder": -6597606703104,
        "kind": "TASK",
        "isOwner": true,
        "permission": null,
        "teamId": null,
        "muted": false,
        "closed": null,
        "inAll": true,
        "viewMode": "list",
        "sortType": "priority",
        "sortOption": {
            "groupBy": "none",
            "orderBy": "priority"
        }
    }
]
```

### Python示例代码
```python
def get_projects(self) -> List[Dict]:
    """
    获取所有项目列表
    
    Returns:
        List[Dict]: 项目列表
        
    Raises:
        Exception: 当获取失败时
    """
    url = "https://dida365.com/api/v2/project/all"
    
    try:
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"获取项目列表失败: {str(e)}")
```

## 创建项目

### 基本信息
- 接口名称：创建项目
- 接口描述：创建一个新的项目
- 请求方法：POST
- 请求URL：/project
- 请求参数格式：application/json

### 请求参数
详细的项目字段说明请参考 [项目字段说明](../data/project.md)。

基本字段示例：
```json
{
    "name": "新项目",
    "color": "#FF6161",
    "sortOrder": -6597606703104,
    "kind": "TASK"
}
```

### Python示例代码
```python
def create_project(self, project_data: Dict) -> Dict:
    """
    创建新项目
    
    Args:
        project_data: 项目数据
        
    Returns:
        Dict: 创建的项目数据
        
    Raises:
        Exception: 当创建失败时
    """
    url = "https://dida365.com/api/v2/project"
    
    try:
        response = requests.post(url, json=project_data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"创建项目失败: {str(e)}")
```

## 更新项目

### 基本信息
- 接口名称：更新项目
- 接口描述：更新现有项目
- 请求方法：POST
- 请求URL：/project/{projectId}
- 请求参数格式：application/json

### 请求参数
与创建项目接口相同，但需要包含项目ID。

### Python示例代码
```python
def update_project(self, project_id: str, project_data: Dict) -> Dict:
    """
    更新项目
    
    Args:
        project_id: 项目ID
        project_data: 更新的项目数据
        
    Returns:
        Dict: 更新后的项目数据
        
    Raises:
        Exception: 当更新失败时
    """
    url = f"https://dida365.com/api/v2/project/{project_id}"
    
    try:
        response = requests.post(url, json=project_data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"更新项目失败: {str(e)}")
```

## 删除项目

### 基本信息
- 接口名称：删除项目
- 接口描述：删除指定项目
- 请求方法：DELETE
- 请求URL：/project/{projectId}

### Python示例代码
```python
def delete_project(self, project_id: str) -> bool:
    """
    删除项目
    
    Args:
        project_id: 项目ID
        
    Returns:
        bool: 是否删除成功
        
    Raises:
        Exception: 当删除失败时
    """
    url = f"https://dida365.com/api/v2/project/{project_id}"
    
    try:
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        raise Exception(f"删除项目失败: {str(e)}")
```

## 完整示例

### 项目管理类
```python
class ProjectManager:
    def __init__(self, token: str):
        self.processor = DidaTaskProcessor(token)
        
    def list_projects(self) -> None:
        """列出所有项目"""
        try:
            projects = self.processor.get_projects()
            print(f"获取成功: {len(projects)}个项目")
            for project in projects:
                print(f"- {project['name']} ({project['id']})")
        except Exception as e:
            print(f"获取项目失败: {str(e)}")
            
    def add_project(self, name: str, **kwargs) -> Dict:
        """添加新项目"""
        project_data = {
            "name": name,
            "color": "#FF6161",  # 默认颜色
            "kind": "TASK",      # 默认类型
            **kwargs
        }
        try:
            project = self.processor.create_project(project_data)
            print(f"创建项目成功: {project['name']}")
            return project
        except Exception as e:
            print(f"创建项目失败: {str(e)}")
            return {}
            
    def archive_project(self, project_id: str) -> bool:
        """归档项目"""
        try:
            project = self.processor.update_project(project_id, {"closed": True})
            print(f"归档项目成功: {project['name']}")
            return True
        except Exception as e:
            print(f"归档项目失败: {str(e)}")
            return False

# 使用示例
manager = ProjectManager("your-token")

# 列出所有项目
manager.list_projects()

# 创建项目
project = manager.add_project(
    name="新项目",
    color="#4A90E2"  # 自定义颜色
)

# 归档项目
if project:
    manager.archive_project(project["id"])
```

### 注意事项
1. 项目管理
   - 合理组织项目结构
   - 避免创建过多项目
   - 及时归档不活跃项目

2. 数据安全
   - 备份重要项目数据
   - 谨慎删除项目
   - 控制项目访问权限

3. 最佳实践
   - 使用有意义的项目名称
   - 合理设置项目颜色
   - 定期整理项目列表 