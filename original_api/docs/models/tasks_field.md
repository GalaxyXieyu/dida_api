# 滴答清单任务字段说明文档

## 任务关键字段汇总
下表汇总了任务中最重要的业务字段，按照实际使用频率和重要性排序：

### 任务核心字段
| 字段名 | 类型 | 说明 | 示例值 | 业务含义 |
|--------|------|------|---------|----------|
| id | string | 任务ID | "67a9f85de4b06f0b57e3d7dc" | 任务的唯一标识 |
| title | string | 任务标题 | "完成产品设计" | 任务的核心内容 |
| content | string | 任务描述 | "需要完成产品的整体设计方案..." | 任务的详细说明 |
| status | integer | 任务状态 | 0 | 0:待办, 2:已完成 |
| priority | integer | 优先级 | 5 | 1-5，值越大优先级越高 |
| progress | float | 完成进度 | 0.75 | 任务完成度（0-1） |
| startDate | string | 开始时间 | "2024-02-10T13:00:00.000+0000" | 任务开始时间 |
| dueDate | string | 截止时间 | "2024-02-10T13:00:00.000+0000" | 任务必须完成的时间点 |
| isAllDay | boolean | 是否全天任务 | false | 标识是否为全天任务 |
| timeZone | string | 时区 | "Asia/Shanghai" | 任务时间的时区设置 |
| createdTime | string | 创建时间 | "2024-02-10T13:00:13.231+0000" | 任务创建的时间戳 |
| modifiedTime | string | 修改时间 | "2024-02-10T13:02:41.000+0000" | 最后修改的时间戳 |
| creator | integer | 创建者ID | 1014518876 | 任务创建者 |
| completedUserId | string | 完成者ID | null | 标识谁完成了任务 |
| projectId | string | 所属项目ID | "inbox1014518876" | 任务所属的项目 |
| columnId | string | 看板列ID | "65db218c7ae46e15dac5def8" | 看板视图中的列位置 |
| parentId | string | 父任务ID | null | 子任务关联的父任务 |
| childIds | array | 子任务ID列表 | [] | 父任务关联的子任务列表 |
| items | array | 子任务列表 | [{"title": "子任务1", "status": 0}] | 任务的子任务清单 |
| tags | array | 标签列表 | ["工作", "重要"] | 任务的分类标签 |
| reminders | array | 提醒时间 | ["2024-02-10T09:00:00.000+0000"] | 任务的提醒时间点 |
| attachments | array | 附件列表 | [{"fileName": "设计文档.pdf"}] | 任务相关的文件 |
| repeatTaskId | string | 重复任务ID | null | 重复任务的标识 |
| repeatFlag | string | 重复标志 | null | 重复规则标识 |
| repeatFirstDate | string | 首次重复日期 | null | 重复任务的开始日期 |
| sortOrder | integer | 排序顺序 | -1099511627776 | 控制任务显示顺序 |
| kind | string | 任务类型 | "TEXT" | 标识任务的类型 |
| etag | string | 版本标识 | "ev6iv2ke" | 任务版本控制 |
| commentCount | integer | 评论数量 | 0 | 任务的评论数 |
| focusSummaries | array | 专注记录 | [] | 专注模式使用记录 |
| pomodoroSummaries | array | 番茄钟记录 | [] | 番茄工作法记录 |

本文档详细说明了滴答清单任务数据中的各个字段含义，按照重要性和使用频率进行分类。

## 核心必要字段（最常用）
| 字段名 | 类型 | 说明 | 示例值 | 使用场景 |
|--------|------|------|---------|----------|
| id | string | 任务唯一标识符 | "67a9f85de4b06f0b57e3d7dc" | 用于标识和操作特定任务 |
| projectId | string | 所属项目ID | "inbox1014518876" | 标识任务所属的项目 |

## 时间相关字段（重要）
| 字段名 | 类型 | 说明 | 示例值 | 使用场景 |
|--------|------|------|---------|----------|
| startDate | string | 开始时间 | "2024-02-10T13:00:00.000+0000" | 任务开始时间 |
| createdTime | string | 创建时间 | "2024-02-10T13:00:13.231+0000" | 任务创建的时间戳 |
| modifiedTime | string | 修改时间 | "2024-02-10T13:02:41.000+0000" | 最后修改的时间戳 |
| timeZone | string | 时区 | "Asia/Shanghai" | 任务时间的时区设置 |
| isAllDay | boolean | 是否全天任务 | false | 标识是否为全天任务 |

## 组织与分类字段（常用）
| 字段名 | 类型 | 说明 | 示例值 | 使用场景 |
|--------|------|------|---------|----------|
| sortOrder | integer | 排序顺序 | -1099511627776 | 控制任务显示顺序 |
| kind | string | 任务类型 | "TEXT" | 标识任务的类型 |
| columnId | string | 看板列ID | "65db218c7ae46e15dac5def8" | 看板视图中的列位置 |

## 提醒与重复字段（功能性）
| 字段名 | 类型 | 说明 | 示例值 | 使用场景 |
|--------|------|------|---------|----------|
| repeatTaskId | string | 重复任务ID | null | 重复任务的标识 |
| repeatFlag | string | 重复标志 | null | 重复规则标识 |
| repeatFirstDate | string | 首次重复日期 | null | 重复任务的开始日期 |

## 关联字段（结构性）
| 字段名 | 类型 | 说明 | 示例值 | 使用场景 |
|--------|------|------|---------|----------|
| parentId | string | 父任务ID | null | 子任务关联的父任务 |
| childIds | array | 子任务ID列表 | [] | 父任务关联的子任务列表 |
| attachments | array | 附件列表 | [] | 任务的附件信息 |

## 用户相关字段（管理性）
| 字段名 | 类型 | 说明 | 示例值 | 使用场景 |
|--------|------|------|---------|----------|
| creator | integer | 创建者ID | 1014518876 | 任务创建者 |
| completedUserId | string | 完成者ID | null | 标识谁完成了任务 |
| etag | string | 版本标识 | "ev6iv2ke" | 任务版本控制 |

## 统计字段（辅助性）
| 字段名 | 类型 | 说明 | 示例值 | 使用场景 |
|--------|------|------|---------|----------|
| commentCount | integer | 评论数量 | 0 | 任务的评论数 |
| focusSummaries | array | 专注记录 | [] | 专注模式使用记录 |
| pomodoroSummaries | array | 番茄钟记录 | [] | 番茄工作法记录 |

## 使用说明

1. **核心必要字段**：这些字段是每个任务必须具备的基本信息，在创建和更新任务时必须关注。

2. **时间相关字段**：对于任务管理和规划非常重要，特别是在设置任务截止日期和跟踪任务进度时。

3. **组织与分类字段**：帮助用户更好地管理和查找任务，在大量任务管理时特别有用。

4. **其他字段**：根据具体使用场景和需求选择性使用，不是所有字段都需要在每个任务中使用。

## 注意事项

1. 所有时间字段都使用ISO 8601格式的UTC时间。
2. 优先级范围是1-5，其中5代表最高优先级。
3. 任务状态目前只有两种：0（未完成）和2（已完成）。
4. 标签、附件等数组类型的字段，如果为空则显示为[]。
5. 某些字段可能为null，表示该功能未被使用。

## 项目字段 (Project Fields)

### 基本信息
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| id_project | string | 项目唯一标识符 | "ef68424f99ef959ef1218e4e" |
| name | string | 项目名称 | "工作" |
| color | string | 项目颜色 | "#FF6161" |
| kind_project | string | 项目类型 | "TASK" |

### 权限与状态
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| isOwner | boolean | 是否为项目所有者 | true |
| permission | string | 权限设置 | null |
| teamId | string | 团队ID | null |
| muted | boolean | 是否静音通知 | false |
| closed | boolean | 是否关闭 | null |

### 显示与排序
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| inAll | boolean | 是否显示在"所有"视图 | true |
| sortOrder_project | integer | 项目排序顺序 | -6597606703104 |
| viewMode | string | 视图模式 | "list" |
| sortType | string | 排序类型 | "priority" |
| sortOption | object | 排序选项 | {"groupBy": "none", "orderBy": "priority"} |

## 项目组字段 (Project Group Fields)

### 基本信息
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| id_group | string | 项目组唯一标识符 | "ef5d4ac580f4e7842aaa4337" |
| name_group | string | 项目组名称 | "笔记汇总" |
| showAll | boolean | 是否显示所有项目 | true |

### 显示与排序
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| sortOrder_group | integer | 项目组排序顺序 | 10720238370816 |
| viewMode_group | string | 视图模式 | "list" |
| sortType_group | string | 排序类型 | "project" |
| sortOption_group | object | 排序选项 | {"groupBy": "project", "orderBy": "createdTime"} |

## 计算字段 (Computed Fields)

这些字段是在数据处理过程中添加的，用于方便查询和显示：

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|---------|
| tag_names | string | 标签名称（逗号分隔） | "工作,重要" |
| attachment_count | integer | 附件数量 | 0 |
| attachment_ids | string | 附件ID（逗号分隔） | "" |
| reminder_times | string | 提醒时间（逗号分隔） | "" |
| subtask_count | integer | 子任务数量 | 0 |
| tag_colors | string | 标签颜色（逗号分隔） | "#FF6161,#E3CE7B" |
| tag_sort_orders | string | 标签排序顺序（逗号分隔） | "0,-65536" | 