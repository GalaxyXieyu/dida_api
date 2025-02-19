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

## 详细文档

### 任务和笔记的数据结构
```python
{
    'id': '任务或笔记ID',
    'title': '标题',
    'content': '内容',
    'priority': 优先级(0-5),
    'status': 状态(0-未完成, 2-已完成),
    'startDate': '开始时间',
    'dueDate': '截止时间',
    'projectName': '所属项目名称',
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
    'progress': '进度(0-100)'
}
```

### 筛选条件说明
获取任务或笔记时可以使用以下筛选条件：
```python
filters = {
    'status': 0,  # 任务状态 (0-未完成, 2-已完成)
    'priority': 3,  # 优先级 (0-5)
    'project_id': 'xxx',  # 项目ID
    'tag_names': ['标签1', '标签2'],  # 标签名称列表
    'start_date': '2024-02-19T00:00:00.000+0000',  # 开始时间
    'due_date': '2024-02-20T00:00:00.000+0000'  # 截止时间
}

# 使用筛选条件获取任务
tasks = client.tasks.get_all_tasks(filters)

# 使用筛选条件获取笔记
notes = client.tasks.get_all_notes(filters)
```

## 版本历史

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