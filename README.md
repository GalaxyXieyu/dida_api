# 滴答清单 Python SDK

这是一个非官方的滴答清单(TickTick/Dida365) Python SDK，用于访问滴答清单的API。

## 安装

```bash
# 使用指定源安装（推荐）
pip install didatodolist --index-url https://pypi.org/simple

# 或者直接安装（如果默认源访问不了，请使用上面的命令）
pip install didatodolist
```

## 快速开始

### 导入必要的类
```python
from dida import DidaClient  # 导入所需的所有类
```

### 客户端初始化和认证
```python
# 方式1：使用邮箱密码初始化
client = DidaClient(email="your_email@example.com", password="your_password")
# 获取token（如果你需要保存下来下次使用）
token = client.token
print(f"你的token是: {token}")

# 方式2：使用已有token初始化（推荐，避免多次登录）
client = DidaClient(token="your_token")
```

### 基础使用

```python
# 获取所有任务
tasks = client.tasks.get_all_tasks()

# 获取所有笔记
notes = client.tasks.get_all_notes()

# 创建任务
task = client.tasks.create_task({
    'title': '测试任务',
    'content': '任务详细内容',
    'priority': 3  # 优先级：0-最低，1-低，3-中，5-高
})

# 创建笔记
note = client.tasks.create_note({
    'title': '测试笔记',
    'content': '笔记内容'
})

# 更新任务
task = client.tasks.update_task(task['id'], {
    'title': '更新后的任务标题',
    'content': '更新后的内容'
})

# 更新笔记
note = client.tasks.update_note(note['id'], {
    'title': '更新后的笔记标题',
    'content': '更新后的内容'
})

# 删除任务或笔记
client.tasks.delete(item_id, project_id)
```

### 任务分析和统计功能

#### 1. 按时间范围查询任务

```python
# 获取今天的任务
today_tasks = client.tasks.get_today_tasks()
# 返回格式：{'已完成': [...], '未完成': [...]}

# 获取本周的任务
week_tasks = client.tasks.get_this_week_tasks()

# 获取本月的任务
month_tasks = client.tasks.get_this_month_tasks()

# 获取未来7天的任务
next_7_days_tasks = client.tasks.get_next_7_days_tasks()

# 获取过期任务
overdue_tasks = client.tasks.get_overdue_tasks()
```

#### 2. 按优先级查询任务

```python
# 获取所有高优先级任务
high_priority_tasks = client.tasks.get_tasks_by_priority(priority=5)

# 获取所有中优先级任务
medium_priority_tasks = client.tasks.get_tasks_by_priority(priority=3)

# 获取所有低优先级任务
low_priority_tasks = client.tasks.get_tasks_by_priority(priority=1)

# 获取所有最低优先级任务
lowest_priority_tasks = client.tasks.get_tasks_by_priority(priority=0)
```

#### 3. 获取任务统计信息

```python
# 获取任务统计信息
stats = client.tasks.get_task_statistics()

# 统计信息包括：
print(f"总任务数: {stats['total_tasks']}")
print(f"已完成任务数: {stats['completed_tasks']}")
print(f"未完成任务数: {stats['uncompleted_tasks']}")
print(f"过期任务数: {stats['overdue_tasks']}")
print(f"各优先级任务数: {stats['priority_stats']}")
print(f"今日完成率: {stats['today_completion_rate']}%")
print(f"本周完成率: {stats['week_completion_rate']}%")
print(f"本月完成率: {stats['month_completion_rate']}%")
```

#### 4. 获取任务趋势数据

```python
# 获取最近30天的任务趋势
trends = client.tasks.get_task_trends(days=30)

# 趋势数据包括：
print("日期列表:", trends['dates'])
print("每日完成数:", trends['completed_counts'])
print("每日新建数:", trends['created_counts'])
print("每日完成率:", trends['completion_rates'])

# 可以用这些数据绘制趋势图，例如使用matplotlib：
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(trends['dates'], trends['completion_rates'], marker='o')
plt.title('任务完成率趋势')
plt.xlabel('日期')
plt.ylabel('完成率(%)')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()
```

### 任务重复规则说明
任务可以设置不同类型的重复规则，支持以下几种方式：

```python
# 1. 每天重复
task = client.tasks.create_task({
    'title': '每日任务',
    'content': '这是一个每天重复的任务',
    'startDate': '2025-02-20T09:00:00.000+0000',
    'repeatFlag': '每天'
})

# 2. 每周重复（使用开始日期的星期几）
task = client.tasks.create_task({
    'title': '每周任务',
    'startDate': '2025-02-20T09:00:00.000+0000',  # 如果是周三创建，则每周三重复
    'repeatFlag': '每周'
})

# 3. 每月重复（使用开始日期的日期）
task = client.tasks.create_task({
    'title': '每月任务',
    'startDate': '2025-02-20T09:00:00.000+0000',  # 如果20号创建，则每月20号重复
    'repeatFlag': '每月'
})

# 4. 每年重复（使用开始日期的月份和日期）
task = client.tasks.create_task({
    'title': '每年任务',
    'startDate': '2025-02-20T09:00:00.000+0000',  # 如果2月20日创建，则每年2月20日重复
    'repeatFlag': '每年'
})

# 5. 每周工作日（周一至周五）
task = client.tasks.create_task({
    'title': '工作日任务',
    'startDate': '2025-02-20T09:00:00.000+0000',
    'repeatFlag': '每周工作日'
})

# 6. 法定工作日（跳过节假日和周末）
task = client.tasks.create_task({
    'title': '法定工作日任务',
    'startDate': '2025-02-20T09:00:00.000+0000',
    'repeatFlag': '法定工作日'
})

# 7. 艾宾浩斯记忆法
task = client.tasks.create_task({
    'title': '记忆任务',
    'startDate': '2025-02-20T09:00:00.000+0000',
    'repeatFlag': '艾宾浩斯记忆法'
})

# 8. 自定义重复规则（高级用法）
task = client.tasks.create_task({
    'title': '自定义重复任务',
    'startDate': '2025-02-20T09:00:00.000+0000',
    'repeatFlag': 'RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR',
    'repeatFrom': '2'
})
```

重复规则参数说明：

1. 基础重复规则：
   - `每天`: 每天重复一次
   - `每周`: 每周重复一次，重复日期与任务开始日期的星期几相同
   - `每月`: 每月重复一次，重复日期与任务开始日期的日期相同
   - `每年`: 每年重复一次，重复日期与任务开始日期的月份和日期相同
   - `每周工作日`: 周一至周五每天重复
   - `法定工作日`: 跳过节假日和周末
   - `艾宾浩斯记忆法`: 按照记忆曲线进行重复

2. 重要说明：
   - 每周重复：会自动使用任务开始日期的星期几作为重复日期
   - 每月重复：会自动使用任务开始日期的日期作为重复日期
   - 每年重复：会自动使用任务开始日期的月份和日期作为重复日期

3. 其他重要参数：
   - startDate: 开始时间，必须使用 ISO 8601 格式（YYYY-MM-DDTHH:mm:ss.SSSZ）
   - timeZone: 时区，建议使用 'Asia/Shanghai'

注意事项：
1. 所有重复规则都会自动处理：
   - 设置正确的重复规则格式
   - 设置合适的重复起始时间
   - 处理时区设置
2. 修改重复规则可能会影响已经生成的重复实例
3. 对于特殊情况，可以使用自定义重复规则（RRULE格式）

## 详细文档

### 任务和笔记的数据结构
```python
{
    'id': '任务或笔记ID',
    'title': '标题',
    'content': '内容',
    'priority': 优先级(0-5),
    'status': 状态(0-未完成, 2-已完成),
    'startDate': '开始时间 (YYYY-MM-DD HH:MM:SS)',
    'dueDate': '截止时间 (YYYY-MM-DD HH:MM:SS)',
    'projectName': '所属项目名称',
    'projectId': '项目ID',
    'projectKind': '项目类型(TASK/NOTE)',
    'tagDetails': [  # 标签详情
        {
            'name': '标签名称',
            'label': '标签显示名称'
        }
    ],
    'kind': '类型(TEXT/NOTE)',
    'isAllDay': '是否全天',
    'reminder': '提醒设置',
    'repeatFlag': '重复设置',
    'items': '子项目列表',
    'progress': '进度(0-100)',
    'modifiedTime': '修改时间 (YYYY-MM-DD HH:MM:SS)',
    'createdTime': '创建时间 (YYYY-MM-DD HH:MM:SS)',
    'completedTime': '完成时间 (YYYY-MM-DD HH:MM:SS)',
    'completedUserId': '完成用户ID',
    'isCompleted': '是否已完成(true/false)'
}
```

### 筛选条件说明
获取任务或笔记时可以使用以下筛选条件：
```python
filters = {
    # 基础筛选
    'status': 0,  # 任务状态 (0-未完成, 2-已完成)
    'priority': 3,  # 优先级 (0-最低, 1-低, 3-中, 5-高)
    'project_id': 'xxx',  # 项目ID
    'project_name': '工作',  # 项目名称（支持模糊匹配）
    'column_id': 'xxx',  # 看板列ID
    
    # 标签筛选
    'tag_names': ['工作', '重要'],  # 包含任意一个标签即可（OR关系）
    'tag_names_all': ['工作', '重要'],  # 必须包含所有标签（AND关系）
    
    # 日期筛选
    'start_date': '2024-02-19 00:00:00',  # 开始时间
    'due_date': '2024-02-20 00:00:00',  # 截止时间
    'has_due_date': True,  # 是否有截止时间
    'has_start_date': True,  # 是否有开始时间
    
    # 完成状态筛选
    'is_completed': True,  # 是否已完成
    
    # 进度筛选
    'min_progress': 50,  # 最小进度
    'max_progress': 100,  # 最大进度
    
    # 模糊搜索
    'keyword': '会议',  # 关键词（会搜索标题、内容、项目名称和标签）
    
    # 创建时间筛选
    'created_after': '2024-02-19 00:00:00',  # 在此时间后创建
    'created_before': '2024-02-20 00:00:00',  # 在此时间前创建
    
    # 修改时间筛选
    'modified_after': '2024-02-19 00:00:00',  # 在此时间后修改
    'modified_before': '2024-02-20 00:00:00',  # 在此时间前修改
    
    # 子任务筛选
    'has_items': True,  # 是否有子任务
    'min_items': 1,  # 最少子任务数
    'max_items': 5  # 最多子任务数
}

# 使用筛选条件获取任务
tasks = client.tasks.get_all_tasks(filters)
```

### 筛选示例

1. 标签筛选示例：
```python
# 搜索包含"工作"或"重要"任意一个标签的任务
tasks = client.tasks.get_all_tasks({
    'tag_names': ['工作', '重要']
})

# 搜索同时包含"工作"和"重要"两个标签的任务
tasks = client.tasks.get_all_tasks({
    'tag_names_all': ['工作', '重要']
})

# 也支持单个标签筛选
tasks = client.tasks.get_all_tasks({
    'tag_names': '工作'  # 或 'tag_names_all': '工作'
})

# 标签筛选可以和其他条件组合
tasks = client.tasks.get_all_tasks({
    'tag_names': ['工作', '重要'],
    'is_completed': False,
    'priority': 5
})
```

2. 按优先级和状态筛选：
```python
# 获取所有高优先级且未完成的任务
tasks = client.tasks.get_all_tasks({
    'priority': 5,
    'is_completed': False
})

# 获取所有已完成的中优先级任务
tasks = client.tasks.get_all_tasks({
    'priority': 3,
    'is_completed': True
})
```

3. 按日期范围筛选：
```python
# 获取特定日期范围内的任务
tasks = client.tasks.get_all_tasks({
    'created_after': '2024-02-19 00:00:00',
    'created_before': '2024-02-20 00:00:00'
})

# 获取最近修改的任务
tasks = client.tasks.get_all_tasks({
    'modified_after': '2024-02-19 00:00:00'
})
```

4. 按进度筛选：
```python
# 获取进度超过50%的任务
tasks = client.tasks.get_all_tasks({
    'min_progress': 50
})

# 获取进度在30%-70%之间的任务
tasks = client.tasks.get_all_tasks({
    'min_progress': 30,
    'max_progress': 70
})
```

5. 复合条件筛选：
```python
# 获取工作项目中的高优先级、有截止日期且未完成的任务
tasks = client.tasks.get_all_tasks({
    'project_name': '工作',
    'priority': 5,
    'has_due_date': True,
    'is_completed': False
})

# 获取包含特定标签且有子任务的任务
tasks = client.tasks.get_all_tasks({
    'tag_names': ['重要', '工作'],
    'has_items': True
})
```

6. 看板相关筛选：
```python
# 获取特定看板列的任务
tasks = client.tasks.get_all_tasks({
    'column_id': 'xxx'
})

# 获取特定项目中未完成的看板任务
tasks = client.tasks.get_all_tasks({
    'project_id': 'xxx',
    'column_id': 'xxx',
    'is_completed': False
})
```

## 版本历史

### 0.1.10 (2024-02-19)
- 修复任务完成状态判断逻辑
  - 同时检查 completedTime 和 completedUserId
  - 优化日期格式解析
  - 改进任务筛选流程

### 0.1.9 (2024-02-19)
- 修复任务筛选功能中的缩进错误
- 优化代码结构
- 添加自动发布功能
  - 支持通过 git commit 触发自动发布
  - 自动递增版本号
  - 自动构建和发布到 PyPI

### 0.1.8 (2024-02-19)
- 重构任务完成状态相关功能
  - 新增专门的已完成任务获取接口
  - 优化任务完成状态判断逻辑
  - 改进任务统计和分析功能
- 数据结构优化
  - 添加完成时间和完成用户ID字段
  - 移除不必要的栏目状态判断
  - 提升代码性能和可维护性

### 0.1.7 (2024-02-19)
- 添加任务分析和统计功能
  - 按时间范围查询任务（今天/本周/本月/未来7天）
  - 按优先级查询任务
  - 获取任务统计信息
  - 获取任务趋势数据
  - 支持任务完成率统计和趋势分析
  - 支持过期任务查询
- 优化代码结构和性能
- 完善文档和使用示例

### 0.1.6 (2024-02-19)
- 改进任务完成状态判断逻辑
  - 新增栏目信息管理，通过栏目状态判断任务是否完成
  - 支持看板视图中的任务状态判断
  - 修复任务完成状态判断不准确的问题
- 优化代码结构
  - 重构任务分组方法，使用更清晰的英文键名
  - 改进栏目信息的存储和管理
  - 提升代码可维护性

### 0.1.5 (2024-02-19)
- 添加任务分析和统计功能
  - 按时间范围查询任务（今天/本周/本月/未来7天）
  - 按优先级查询任务
  - 获取任务统计信息
  - 获取任务趋势数据
  - 支持任务完成率统计和趋势分析
  - 支持过期任务查询
- 优化代码结构和性能
- 完善文档和使用示例

### 0.1.4 (2024-02-19)
- 分离任务和笔记的API操作
- 简化数据结构，只保留必要字段
- 合并项目和标签信息到返回数据中
- 优化筛选功能
- 改进API文档和使用示例

### 0.1.3 (2024-02-18)
- 添加更多任务字段支持
- 完善文档说明
- 添加Python 3.11支持

### 0.1.2 (2024-02-15)
- 初始版本发布
- 基本的任务、项目、标签管理功能

## 注意事项

1. 任务和笔记的区别：
   - 任务(TEXT)：支持完成状态、优先级、提醒等功能
   - 笔记(NOTE)：主要用于记录信息，不支持完成状态和提醒

2. 数据结构已经过优化：
   - 移除了不必要的字段（如排序、ID等）
   - 添加了更有意义的字段（如项目名称、标签详情等）
   - 保持数据结构的简洁性和可读性

3. API调用建议：
   - 使用token方式认证，避免频繁登录
   - 合理使用筛选条件，减少数据传输
- 注意API调用频率限制

4. 任务分析和统计功能使用建议：
   - 定期查看任务统计信息，了解整体任务完成情况
   - 使用趋势数据分析工作效率变化
   - 及时处理过期任务
   - 合理安排高优先级任务

## 许可证
MIT License

## 联系方式
- 作者：xieyu
- 邮箱：523018705@qq.com 