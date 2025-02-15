# 标签管理接口

## 获取标签列表

### 基本信息
- 接口名称：获取标签列表
- 接口描述：获取用户的所有标签列表
- 请求方法：GET
- 请求URL：/tag/all
- 请求参数格式：无

### 响应数据结构
```json
[
    {
        "name": "工作",
        "label": "工作",
        "sortOrder": 0,
        "color": "#FF6161",
        "sortType": "manual"
    },
    {
        "name": "重要",
        "label": "重要",
        "sortOrder": -65536,
        "color": "#E3CE7B",
        "sortType": "manual"
    }
]
```

### Python示例代码
```python
def get_tags(self) -> List[Dict]:
    """
    获取所有标签列表
    
    Returns:
        List[Dict]: 标签列表
        
    Raises:
        Exception: 当获取失败时
    """
    url = "https://dida365.com/api/v2/tag/all"
    
    try:
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"获取标签列表失败: {str(e)}")
```

## 创建标签

### 基本信息
- 接口名称：创建标签
- 接口描述：创建一个新的标签
- 请求方法：POST
- 请求URL：/tag
- 请求参数格式：application/json

### 请求参数
详细的标签字段说明请参考 [标签字段说明](../data/tag.md)。

基本字段示例：
```json
{
    "name": "新标签",
    "color": "#FF6161",
    "sortOrder": 0,
    "sortType": "manual"
}
```

### Python示例代码
```python
def create_tag(self, tag_data: Dict) -> Dict:
    """
    创建新标签
    
    Args:
        tag_data: 标签数据
        
    Returns:
        Dict: 创建的标签数据
        
    Raises:
        Exception: 当创建失败时
    """
    url = "https://dida365.com/api/v2/tag"
    
    try:
        response = requests.post(url, json=tag_data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"创建标签失败: {str(e)}")
```

## 更新标签

### 基本信息
- 接口名称：更新标签
- 接口描述：更新现有标签
- 请求方法：POST
- 请求URL：/tag/{tagName}
- 请求参数格式：application/json

### 请求参数
与创建标签接口相同，但需要在URL中指定标签名称。

### Python示例代码
```python
def update_tag(self, tag_name: str, tag_data: Dict) -> Dict:
    """
    更新标签
    
    Args:
        tag_name: 标签名称
        tag_data: 更新的标签数据
        
    Returns:
        Dict: 更新后的标签数据
        
    Raises:
        Exception: 当更新失败时
    """
    url = f"https://dida365.com/api/v2/tag/{tag_name}"
    
    try:
        response = requests.post(url, json=tag_data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"更新标签失败: {str(e)}")
```

## 删除标签

### 基本信息
- 接口名称：删除标签
- 接口描述：删除指定标签
- 请求方法：DELETE
- 请求URL：/tag/{tagName}

### Python示例代码
```python
def delete_tag(self, tag_name: str) -> bool:
    """
    删除标签
    
    Args:
        tag_name: 标签名称
        
    Returns:
        bool: 是否删除成功
        
    Raises:
        Exception: 当删除失败时
    """
    url = f"https://dida365.com/api/v2/tag/{tag_name}"
    
    try:
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        raise Exception(f"删除标签失败: {str(e)}")
```

## 完整示例

### 标签管理类
```python
class TagManager:
    def __init__(self, token: str):
        self.processor = DidaTaskProcessor(token)
        
    def list_tags(self) -> None:
        """列出所有标签"""
        try:
            tags = self.processor.get_tags()
            print(f"获取成功: {len(tags)}个标签")
            for tag in tags:
                print(f"- {tag['name']} ({tag['color']})")
        except Exception as e:
            print(f"获取标签失败: {str(e)}")
            
    def add_tag(self, name: str, **kwargs) -> Dict:
        """添加新标签"""
        tag_data = {
            "name": name,
            "color": "#FF6161",  # 默认颜色
            "sortType": "manual", # 默认排序类型
            **kwargs
        }
        try:
            tag = self.processor.create_tag(tag_data)
            print(f"创建标签成功: {tag['name']}")
            return tag
        except Exception as e:
            print(f"创建标签失败: {str(e)}")
            return {}
            
    def change_tag_color(self, tag_name: str, color: str) -> bool:
        """修改标签颜色"""
        try:
            tag = self.processor.update_tag(tag_name, {"color": color})
            print(f"修改标签颜色成功: {tag['name']} -> {color}")
            return True
        except Exception as e:
            print(f"修改标签颜色失败: {str(e)}")
            return False

# 使用示例
manager = TagManager("your-token")

# 列出所有标签
manager.list_tags()

# 创建标签
tag = manager.add_tag(
    name="重要",
    color="#E3CE7B"  # 自定义颜色
)

# 修改标签颜色
if tag:
    manager.change_tag_color(tag["name"], "#4A90E2")
```

### 注意事项
1. 标签管理
   - 避免创建过多标签
   - 使用有意义的标签名称
   - 合理组织标签体系

2. 标签使用
   - 一个任务可以有多个标签
   - 标签可以跨项目使用
   - 标签便于任务分类和筛选

3. 最佳实践
   - 制定标签命名规范
   - 使用颜色区分标签类型
   - 定期清理无用标签 