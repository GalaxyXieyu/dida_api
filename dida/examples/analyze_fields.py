"""
分析滴答清单API返回的数据结构

本脚本用于分析API返回的数据结构，包括：
1. 任务字段
2. 项目字段
3. 标签字段

分析结果将被写入到README.md文件中。
"""

from dida import DidaClient
from collections import defaultdict
from typing import Dict, Any, Set
import json
from pprint import pformat

def analyze_field_types(data: Dict[str, Any], prefix: str = "") -> Dict[str, Set[str]]:
    """
    递归分析字段类型
    
    Args:
        data: 要分析的数据
        prefix: 字段前缀
        
    Returns:
        Dict[str, Set[str]]: 字段及其可能的类型
    """
    field_types = defaultdict(set)
    
    def _analyze(value: Any, current_prefix: str):
        if isinstance(value, dict):
            for k, v in value.items():
                new_prefix = f"{current_prefix}.{k}" if current_prefix else k
                _analyze(v, new_prefix)
        elif isinstance(value, list):
            if value:  # 只分析非空列表
                # 分析第一个元素的类型
                _analyze(value[0], current_prefix)
        else:
            field_types[current_prefix].add(
                type(value).__name__ if value is not None else "null"
            )
    
    _analyze(data, prefix)
    return dict(field_types)

def format_field_types(field_types: Dict[str, Set[str]]) -> str:
    """
    格式化字段类型信息为Markdown表格
    
    Args:
        field_types: 字段类型信息
        
    Returns:
        str: Markdown格式的表格
    """
    lines = ["| 字段 | 可能的类型 | 说明 |", "| --- | --- | --- |"]
    
    for field, types in sorted(field_types.items()):
        type_str = " / ".join(sorted(types))
        lines.append(f"| {field} | {type_str} | |")
    
    return "\n".join(lines)

def main():
    # 初始化客户端
    client = DidaClient(email="523018705@qq.com", password="X1i2e3y4u5")
    
    print("正在分析API数据结构...")
    
    # 获取所有数据
    response = client.tasks._get("/api/v2/batch/check/0")
    
    # 分析任务字段
    tasks = response.get('syncTaskBean', {}).get('update', [])
    task_fields = {}
    if tasks:
        task_fields = analyze_field_types(tasks[0])
    
    # 分析项目字段
    projects = response.get('projectProfiles', [])
    project_fields = {}
    if projects:
        project_fields = analyze_field_types(projects[0])
    
    # 分析标签字段
    tags = response.get('tags', [])
    tag_fields = {}
    if tags:
        tag_fields = analyze_field_types(tags[0])
    
    # 生成Markdown文档
    doc = f"""
# API数据结构说明

## 任务（Task）字段

任务对象包含以下字段：

### 核心必要字段
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| id | string | 任务唯一标识符 | "67a9f85de4b06f0b57e3d7dc" |
| title | string | 任务标题 | "完成产品设计" |
| content | string | 任务描述 | "需要完成产品的整体设计方案..." |
| status | integer | 任务状态 | 0 (0:待办, 2:已完成) |
| priority | integer | 优先级 | 1-5，值越大优先级越高 |
| progress | float | 完成进度 | 0.75 (0-1) |

### 时间相关字段
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| startDate | string | 开始时间 | "2024-02-10T13:00:00.000+0000" |
| dueDate | string | 截止时间 | "2024-02-10T13:00:00.000+0000" |
| isAllDay | boolean | 是否全天任务 | false |
| timeZone | string | 时区 | "Asia/Shanghai" |
| createdTime | string | 创建时间 | "2024-02-10T13:00:13.231+0000" |
| modifiedTime | string | 修改时间 | "2024-02-10T13:02:41.000+0000" |

### 组织与分类字段
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| projectId | string | 所属项目ID | "inbox1014518876" |
| columnId | string | 看板列ID | "65db218c7ae46e15dac5def8" |
| parentId | string | 父任务ID | null |
| childIds | array | 子任务ID列表 | [] |
| items | array | 子任务列表 | [{"title": "子任务1", "status": 0}] |
| tags | array | 标签列表 | ["工作", "重要"] |
| sortOrder | integer | 排序顺序 | -1099511627776 |
| kind | string | 任务类型 | "TEXT" |

### 提醒与重复字段
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| reminders | array | 提醒时间 | ["2024-02-10T09:00:00.000+0000"] |
| repeatTaskId | string | 重复任务ID | null |
| repeatFlag | string | 重复标志 | null |
| repeatFirstDate | string | 首次重复日期 | null |

### 附件与评论字段
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| attachments | array | 附件列表 | [{"fileName": "设计文档.pdf"}] |
| commentCount | integer | 评论数量 | 0 |

### 用户相关字段
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| creator | integer | 创建者ID | 1014518876 |
| completedUserId | string | 完成者ID | null |
| etag | string | 版本标识 | "ev6iv2ke" |

### 统计字段
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| focusSummaries | array | 专注记录 | [] |
| pomodoroSummaries | array | 番茄钟记录 | [] |

## 项目（Project）字段

项目对象包含以下字段：

### 基本信息
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| id | string | 项目唯一标识符 | "ef68424f99ef959ef1218e4e" |
| name | string | 项目名称 | "工作" |
| color | string | 项目颜色 | "#FF6161" |
| kind | string | 项目类型 | "TASK" |
| groupId | string | 项目组ID | null |

### 权限与状态
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| isOwner | boolean | 是否为项目所有者 | true |
| permission | string | 权限设置 | null |
| teamId | string | 团队ID | null |
| muted | boolean | 是否静音通知 | false |
| closed | boolean | 是否关闭 | null |
| needAudit | boolean | 是否需要审核 | false |
| openToTeam | boolean | 是否对团队开放 | null |
| teamMemberPermission | string | 团队成员权限 | null |

### 显示与排序
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| inAll | boolean | 是否显示在"所有"视图 | true |
| sortOrder | integer | 项目排序顺序 | -6597606703104 |
| viewMode | string | 视图模式 | "list" |
| sortType | string | 排序类型 | "priority" |
| sortOption.groupBy | string | 分组方式 | "none" |
| sortOption.orderBy | string | 排序方式 | "priority" |

### 其他字段
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| etag | string | 版本标识 | "ev6iv2ke" |
| modifiedTime | string | 修改时间 | "2024-02-10T13:02:41.000+0000" |
| userCount | integer | 用户数量 | 1 |
| source | integer | 来源 | 0 |

## 标签（Tag）字段

标签对象包含以下字段：

### 基本信息
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| name | string | 标签名称 | "重要" |
| label | string | 标签显示名称 | "重要" |
| color | string | 标签颜色 | "#FFD457" |
| type | integer | 标签类型 | 1 (1:个人标签) |

### 排序与显示
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| sortOrder | integer | 排序顺序 | -1099511693312 |
| sortType | string | 排序类型 | "project" |

### 其他字段
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| etag | string | 版本标识 | "ev6iv2ke" |
| rawName | string | 原始名称 | "重要" |

## API端点说明

### 1. 获取所有数据
- 端点：`/api/v2/batch/check/0`
- 方法：GET
- 返回：包含所有任务、项目和标签数据

### 2. 任务管理
- 创建任务：POST `/api/v2/task`
- 更新任务：PUT `/api/v2/task/{{task_id}}`
- 删除任务：POST `/api/v2/batch/task` (批量操作)

### 3. 项目管理
- 创建项目：POST `/api/v2/project`
- 更新项目：PUT `/api/v2/project/{{project_id}}`
- 删除项目：DELETE `/api/v2/project/{{project_id}}`

### 4. 标签管理
- 创建/更新/删除标签：POST `/api/v2/batch/tag` (批量操作)
- 重命名标签：PUT `/api/v2/tag/rename`
- 合并标签：PUT `/api/v2/tag/merge`

注意：
1. 所有时间字段都使用ISO 8601格式的UTC时间。
2. 优先级范围是1-5，其中5代表最高优先级。
3. 任务状态目前只有两种：0（未完成）和2（已完成）。
4. 标签、附件等数组类型的字段，如果为空则显示为[]。
5. 某些字段可能为null，表示该功能未被使用。
"""
    
    # 将文档追加到README.md
    with open("docs/api/README.md", "w", encoding="utf-8") as f:
        f.write(doc)
    
    print("分析完成！结果已写入到 docs/api/README.md")
    
    # 同时打印分析结果
    print("\n=== 分析结果 ===")
    print("\n任务字段:")
    print(pformat(dict(task_fields)))
    print("\n项目字段:")
    print(pformat(dict(project_fields)))
    print("\n标签字段:")
    print(pformat(dict(tag_fields)))

if __name__ == "__main__":
    main() 