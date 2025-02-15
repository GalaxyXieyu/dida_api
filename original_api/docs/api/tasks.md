# 任务管理接口

> 📝 **注意**: 任务的所有字段详细说明请参考 [任务字段说明文档](../models/tasks_field.md)

## 任务同步接口

### 基本信息
- 接口名称：批量检查同步
- 接口描述：获取所有任务、项目、标签等数据的同步信息
- 请求方法：GET
- 请求URL：/batch/check/{checkPoint}
- 请求参数格式：URL参数

### 请求参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|---------|
| checkPoint | integer | 是 | 同步时间戳（毫秒） | 1739430306600 |

### 响应数据结构
```json
{
  "checkPoint": 1739430306600,      // 同步时间戳
  "syncTaskBean": {                 // 任务同步数据
    "update": [],                   // 更新的任务
    "delete": [],                   // 删除的任务
    "add": [],                      // 新增的任务
    "empty": false                  // 是否为空
  },
  "projectProfiles": [],            // 项目/清单数据
  "projectGroups": [],              // 项目组数据
  "filters": [],                    // 过滤器数据
  "tags": [],                       // 标签数据
  "syncTaskOrderBean": {            // 任务排序数据
    "taskOrderByDate": {},          // 按日期排序
    "taskOrderByPriority": {},      // 按优先级排序
    "taskOrderByProject": {}        // 按项目排序
  }
}
```

### Python示例代码
```python
from typing import Dict, List, Optional
from datetime import datetime
import requests
from dataclasses import dataclass

@dataclass
class TaskSync:
    """任务同步数据结构"""
    checkPoint: int
    tasks: List[Dict]
    projects: List[Dict]
    tags: List[Dict]

class DidaTaskProcessor:
    """滴答清单任务处理器"""
    
    def __init__(self, token: str):
        """
        初始化任务处理器
        
        Args:
            token: 访问令牌
        """
        self.token = token
        self.headers = {
            "Cookie": f"t={token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
    def get_all_data(self, checkpoint: int = 0) -> TaskSync:
        """
        获取所有同步数据
        
        Args:
            checkpoint: 同步时间戳，默认为0表示获取所有数据
            
        Returns:
            TaskSync: 同步数据对象
            
        Raises:
            Exception: 当网络请求失败时
        """
        url = f"https://dida365.com/api/v2/batch/check/{checkpoint}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            return TaskSync(
                checkPoint=data["checkPoint"],
                tasks=data.get("syncTaskBean", {}).get("update", []),
                projects=data.get("projectProfiles", []),
                tags=data.get("tags", [])
            )
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取数据失败: {str(e)}")
```

### 注意事项
1. 增量同步
   - 记录最后同步时间
   - 只获取变更数据
   - 减少数据传输量

2. 数据处理
   - 合并本地数据
   - 处理数据冲突
   - 保持数据一致性

3. 性能优化
   - 使用适当的缓存策略
   - 批量处理数据
   - 优化网络请求

## 任务操作接口

### 1. 创建任务

#### 基本信息
- 接口名称：创建任务
- 请求方法：POST
- 请求URL：/api/v2/task
- 请求格式：application/json

#### 请求参数
```python
{
    "title": "测试任务",                                    # 必填，任务标题
    "content": "任务描述",                                  # 可选，任务描述
    "project_name": "工作",                                # 可选，项目名称（会自动转换为projectId）
    "projectId": "4024428bac6d182ac68da936",             # 可选，项目ID（如果提供了project_name则不需要）
    "priority": 3,                                        # 可选，优先级(1-5)
    "startDate": "2024-02-20T09:00:00.000+0000",        # 可选，开始时间
    "dueDate": "2024-02-20T18:00:00.000+0000",          # 可选，截止时间
    "tags": ["工作", "重要"],                              # 可选，标签列表
    "isAllDay": false,                                   # 可选，是否全天任务
    "items": [],                                         # 可选，子任务列表
    "reminders": []                                      # 可选，提醒时间列表
}
```

#### Python示例
```python
# 创建任务
task = processor.add_task(
    title="测试任务",
    project_name="工作",  # 自动转换为projectId
    content="任务描述",
    priority=3,
    tags=["工作", "重要"]  # 直接设置标签
)
```

### 2. 更新任务

#### 基本信息
- 接口名称：更新任务
- 请求方法：PUT
- 请求URL：/api/v2/task/{taskId}
- 请求格式：application/json

#### 请求参数
```python
{
    "title": "更新后的标题",                               # 可选，任务标题
    "content": "更新后的描述",                             # 可选，任务描述
    "project_name": "个人",                               # 可选，移动到其他项目
    "priority": 5,                                       # 可选，优先级
    "status": 2,                                        # 可选，任务状态(0:待办, 2:已完成)
    "tags": ["个人", "学习"],                             # 可选，设置新标签（替换现有标签）
    "add_tags": ["紧急", "会议"],                         # 可选，添加新标签（保留现有标签）
    "remove_tags": ["会议"]                              # 可选，移除指定标签
}
```

#### Python示例
```python
# 更新任务
updated_task = processor.update_task(
    task_id="task123",
    project_name="个人",     # 移动到其他项目
    title="新标题",
    priority=5
)

# 标签操作
task = processor.update_task(
    task_id="task123",
    add_tags=["紧急", "会议"],     # 添加新标签
    remove_tags=["工作"]          # 移除标签
)
```

### 3. 删除任务

#### 基本信息
- 接口名称：删除任务
- 请求方法：DELETE
- 请求URL：/api/v2/task/{taskId}

#### Python示例
```python
# 删除任务
is_deleted = processor.delete_task(task_id="task123")
```

### 4. 完成任务

#### 基本信息
- 接口名称：完成任务
- 请求方法：PUT
- 请求URL：/api/v2/task/{taskId}

#### Python示例
```python
# 完成任务
completed_task = processor.complete_task(task_id="task123")
```

### 5. 批量操作

#### 批量添加任务
```python
# 批量添加任务
tasks = [
    {
        "title": "任务1",
        "project_name": "工作",
        "tags": ["重要"]
    },
    {
        "title": "任务2",
        "project_name": "个人",
        "priority": 4
    }
]
results = processor.add_tasks(tasks)
```

#### 批量更新任务
```python
# 批量更新任务
updates = [
    {
        "id": "task123",
        "project_name": "工作",
        "add_tags": ["紧急"]
    },
    {
        "id": "task456",
        "status": 2  # 完成任务
    }
]
results = processor.update_tasks(updates)
```

#### 批量删除任务
```python
# 批量删除任务
task_ids = ["task123", "task456", "task789"]
success = processor.delete_tasks(task_ids)
```

#### 批量完成任务
```python
# 批量完成任务
task_ids = ["task123", "task456", "task789"]
results = processor.complete_tasks(task_ids)
```

## 注意事项

1. 项目操作
   - 可以通过 `project_name` 直接指定项目，无需手动查找项目ID
   - 移动任务到其他项目只需在更新时指定 `project_name`

2. 标签操作
   - 直接设置标签：使用 `tags` 参数（替换现有标签）
   - 添加标签：使用 `add_tags` 参数（保留现有标签）
   - 移除标签：使用 `remove_tags` 参数
   - 标签操作可以与其他更新操作同时进行

3. 时间格式
   - 所有时间字段使用ISO 8601格式
   - 示例：`"2024-02-20T09:00:00.000+0000"`

4. 状态说明
   - 0: 待办
   - 2: 已完成

5. 优先级说明
   - 1-5: 值越大优先级越高

6. 错误处理
   - 200: 操作成功
   - 400: 请求参数错误
   - 401: 未授权
   - 404: 任务不存在

## 批量操作任务

### 接口说明
- 接口地址：`https://api.dida365.com/api/v2/batch/task`
- 请求方法：`POST`
- 功能说明：支持批量添加、更新、删除任务及其附件

### 请求参数
请求体为JSON对象，包含以下字段：

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| add | array | 是 | 需要添加的任务列表 |
| update | array | 是 | 需要更新的任务列表 |
| delete | array | 是 | 需要删除的任务列表 |
| addAttachments | array | 是 | 需要添加的附件列表 |
| updateAttachments | array | 是 | 需要更新的附件列表 |
| deleteAttachments | array | 是 | 需要删除的附件列表 |

### 任务对象字段说明
> 💡 完整的字段说明请参考 [任务字段说明文档](../models/tasks_field.md)

这里仅列出最常用的字段：

#### 核心字段
| 字段名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|---------|
| id | string | 是 | 任务唯一标识 | "67adb9ad266f556eed65b8f0" |
| title | string | 是 | 任务标题 | "测试内容" |
| content | string | 否 | 任务内容 | "任务详细描述" |
| projectId | string | 是 | 所属项目ID | "4024428bac6d182ac68da936" |

#### 时间相关字段
| 字段名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|---------|
| startDate | string | 否 | 开始时间 | "2025-02-13T10:00:00.000+0000" |
| dueDate | string | 否 | 截止时间 | "2025-02-13T10:30:00.000+0000" |
| timeZone | string | 否 | 时区 | "Asia/Shanghai" |
| isAllDay | boolean | 否 | 是否全天任务 | false |
| isFloating | boolean | 否 | 是否浮动任务 | false |

#### 重复任务字段
| 字段名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|---------|
| repeatFlag | string | 否 | 重复规则 | "RRULE:FREQ=DAILY;INTERVAL=1" |
| repeatFirstDate | string | 否 | 首次重复日期 | "2025-02-13T16:00:00.000+0000" |
| repeatFrom | string | 否 | 重复起始点 | "2

