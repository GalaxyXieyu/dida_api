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
from dida import DidaClient, Task, Project, Tag  # 导入所需的所有类
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
# 创建任务
task = client.tasks.create(Task(
    title="测试任务",
    content="任务详细内容",
    priority=3  # 优先级：0-最低，1-低，3-中，5-高
))

# 创建项目
project = client.projects.create(Project(
    name="测试项目",
    color="#FFD324"  # 项目颜色，使用十六进制颜色代码
))

# 创建标签
tag = client.tags.create(Tag(
    name="重要",
    color="#FF0000"  # 标签颜色，使用十六进制颜色代码
))
```

## 详细文档

### Task 类参数说明
- title: 任务标题（必填）
- content: 任务内容（选填）
- priority: 优先级（选填）
  - 0: 最低
  - 1: 低
  - 3: 中
  - 5: 高
- start_date: 开始时间（选填）
- due_date: 截止时间（选填）
- project_id: 所属项目ID（选填）
- tags: 标签列表（选填）

### Project 类参数说明
- name: 项目名称（必填）
- color: 项目颜色（选填，十六进制颜色代码）

### Tag 类参数说明
- name: 标签名称（必填）
- color: 标签颜色（选填，十六进制颜色代码）

## 注意事项

1. 所有的创建操作都需要先实例化对应的模型类（Task、Project、Tag），然后通过client的对应方法创建
2. 颜色值使用标准的十六进制颜色代码（如 "#FF0000" 表示红色）
3. 时间相关的字段支持多种格式，推荐使用 ISO 8601 格式（如 "2024-03-15T10:00:00.000+0000"）

## 项目结构
```
dida/
├── api/                    # API实现目录
│   ├── __init__.py        # API模块初始化
│   ├── base.py            # API基类
│   ├── task.py            # 任务相关API
│   ├── project.py         # 项目相关API
│   └── tag.py             # 标签相关API
├── docs/                   # 文档目录
│   ├── api/               # API文档
│   │   ├── README.md      # API总体说明
│   │   └── ...           # 各API详细文档
│   └── models/            # 数据模型文档
├── examples/              # 示例代码目录
│   ├── basic/            # 基础示例
│   │   └── basic_usage.py # 基础用法示例
│   └── advanced/         # 高级示例
│       ├── task_analytics.py  # 任务分析示例
│       └── advanced_usage.py  # 高级用法示例
├── models/               # 数据模型目录
│   ├── __init__.py      # 模型模块初始化
│   ├── base.py          # 模型基类
│   ├── task.py          # 任务模型
│   ├── project.py       # 项目模型
│   └── tag.py           # 标签模型
├── utils/               # 工具类目录
│   ├── __init__.py      # 工具模块初始化
│   ├── http.py          # HTTP客户端
│   └── auth.py          # 认证相关工具
├── __init__.py          # 包初始化文件
├── client.py            # 主客户端类
└── exceptions.py        # 异常定义
```

## 模块说明

### 1. API模块 (`api/`)
- `base.py`: 定义API基类，包含通用的HTTP请求方法
- `task.py`: 实现任务相关的API调用
- `project.py`: 实现项目相关的API调用
- `tag.py`: 实现标签相关的API调用

### 2. 数据模型 (`models/`)
- `base.py`: 定义模型基类，包含通用的序列化方法
- `task.py`: 任务数据模型，定义任务的属性和方法
- `project.py`: 项目数据模型，定义项目的属性和方法
- `tag.py`: 标签数据模型，定义标签的属性和方法

### 3. 工具类 (`utils/`)
- `http.py`: HTTP客户端实现，处理API请求
- `auth.py`: 认证相关功能，包括token管理

### 4. 示例代码 (`examples/`)
- `basic/`: 基础使用示例
  - `basic_usage.py`: 展示基本的API使用方法
- `advanced/`: 高级使用示例
  - `task_analytics.py`: 任务数据分析示例
  - `advanced_usage.py`: 展示高级功能使用

### 5. 文档 (`docs/`)
- `api/`: API相关文档
  - `README.md`: API总体说明，包含所有字段定义
- `models/`: 数据模型文档，详细说明每个字段的含义和用法

## API功能说明

### 1. 任务管理
- 创建、更新、删除任务
- 获取任务列表
- 任务状态管理
- 子任务管理
- 任务标签管理
- 任务提醒设置
- 重复任务设置

### 2. 项目管理
- 创建、更新、删除项目
- 获取项目列表
- 项目任务管理
- 项目权限管理
- 项目视图设置

### 3. 标签管理
- 创建、更新、删除标签
- 获取标签列表
- 标签重命名
- 标签合并
- 标签任务管理

## 注意事项

### 1. 认证
- 支持邮箱密码和token两种认证方式
- token建议妥善保存，避免泄露
- 建议使用环境变量存储敏感信息

### 2. 错误处理
- 所有API调用都有适当的错误处理
- 使用自定义异常类进行错误分类
- 详细的错误信息便于调试

### 3. 数据类型
- 所有时间字段使用ISO 8601格式的UTC时间
- 优先级范围是1-5，值越大优先级越高
- 任务状态：0（未完成）和2（已完成）

### 4. 性能考虑
- 支持批量操作以提高效率
- 建议合理使用筛选条件减少数据传输
- 注意API调用频率限制

## 贡献指南
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证
MIT License

## 联系方式
- 作者：xieyu
- 邮箱：your_email 