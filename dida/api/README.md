
# API数据结构说明

## 任务（Task）字段

任务对象包含以下字段：

| 字段 | 可能的类型 | 说明 |
| --- | --- | --- |
| content | str | |
| createdTime | str | |
| creator | int | |
| deleted | int | |
| etag | str | |
| id | str | |
| isFloating | bool | |
| kind | str | |
| modifiedTime | str | |
| priority | int | |
| projectId | str | |
| reminder | str | |
| sortOrder | int | |
| status | int | |
| timeZone | str | |
| title | str | |

## 项目（Project）字段

项目对象包含以下字段：

| 字段 | 可能的类型 | 说明 |
| --- | --- | --- |
| barcodeNeedAudit | bool | |
| closed | null | |
| color | str | |
| etag | str | |
| groupId | str | |
| id | str | |
| inAll | bool | |
| isOwner | bool | |
| kind | str | |
| modifiedTime | str | |
| muted | bool | |
| name | str | |
| needAudit | bool | |
| openToTeam | null | |
| permission | null | |
| sortOption.groupBy | str | |
| sortOption.orderBy | str | |
| sortOrder | int | |
| sortType | str | |
| source | int | |
| teamId | null | |
| teamMemberPermission | null | |
| timeline.range | null | |
| timeline.sortOption.groupBy | str | |
| timeline.sortOption.orderBy | str | |
| timeline.sortType | str | |
| transferred | null | |
| userCount | int | |
| viewMode | str | |

## 标签（Tag）字段

标签对象包含以下字段：

| 字段 | 可能的类型 | 说明 |
| --- | --- | --- |
| color | str | |
| etag | str | |
| label | str | |
| name | str | |
| rawName | str | |
| sortOrder | int | |
| sortType | str | |
| type | int | |

## API端点说明

### 1. 获取所有数据
- 端点：`/api/v2/batch/check/0`
- 方法：GET
- 返回：包含所有任务、项目和标签数据

### 2. 任务管理
- 创建任务：POST `/api/v2/task`
- 更新任务：PUT `/api/v2/task/{task_id}`
- 删除任务：POST `/api/v2/batch/task` (批量操作)

### 3. 项目管理
- 创建项目：POST `/api/v2/project`
- 更新项目：PUT `/api/v2/project/{project_id}`
- 删除项目：DELETE `/api/v2/project/{project_id}`

### 4. 标签管理
- 创建/更新/删除标签：POST `/api/v2/batch/tag` (批量操作)
- 重命名标签：PUT `/api/v2/tag/rename`
- 合并标签：PUT `/api/v2/tag/merge`

注意：所有字段的说明将根据实际使用情况持续更新。
