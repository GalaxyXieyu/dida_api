# 滴答清单API教程文档

## 简介
本文档旨在帮助你学习和使用滴答清单(TickTick/Dida)的API。通过这些文档，你可以了解如何通过API来管理你的任务、项目和标签。

## 学习路径

### 1. 基础入门
1. [认证入门](api/auth.md) - 学习如何获取API访问权限
   - 如何登录获取token
   - token的使用方法
   - token的刷新和管理

2. [任务管理基础](api/tasks.md) - 学习任务的基本操作
   - 创建任务（支持直接指定项目名称和标签）
   - 更新任务（包括移动项目、管理标签）
   - 删除和完成任务
   - 批量任务操作
   - 任务查询和过滤

3. [项目管理基础](api/projects.md) - 学习项目的基本操作
   - 创建和管理项目
   - 项目中的任务管理
   - 项目分类和组织

4. [标签管理基础](api/tags.md) - 学习标签的基本操作
   - 创建和管理标签
   - 使用标签组织任务
   - 标签系统的最佳实践

### 2. 数据结构说明
- [任务字段说明](models/tasks_field.md) - 详细了解任务的各个字段
- [项目字段说明](models/projects_field.md) - 详细了解项目的各个字段
- [标签字段说明](models/tags_field.md) - 详细了解标签的各个字段

### 3. 实战应用
查看 [examples](../examples/) 目录下的示例：

1. 基础应用
   - 日常任务管理
     ```python
     # 创建任务示例
     task = processor.add_task(
         title="测试任务",
         project_name="工作",  # 直接指定项目名称
         tags=["重要", "工作"]  # 直接设置标签
     )
     
     # 更新任务示例
     updated_task = processor.update_task(
         task_id="task123",
         project_name="个人",     # 移动到其他项目
         add_tags=["紧急"],       # 添加标签
         remove_tags=["工作"]     # 移除标签
     )
     ```
   - 项目进度跟踪
   - 标签分类管理

2. 高级应用
   - 批量数据处理
     ```python
     # 批量添加任务
     tasks = [
         {"title": "任务1", "project_name": "工作"},
         {"title": "任务2", "project_name": "个人"}
     ]
     results = processor.add_tasks(tasks)
     
     # 批量更新任务
     updates = [
         {"id": "task123", "status": 2},  # 完成任务
         {"id": "task456", "priority": 5}  # 设置优先级
     ]
     results = processor.update_tasks(updates)
     ```
   - 自动化工作流
   - 数据分析和统计

## API调用规范

### 1. 请求格式
- 基础URL: `https://dida365.com/api/v2/`
- 内容类型: `application/json`
- 认证方式: Cookie认证 (`t={token}`)

### 2. 通用参数
所有API请求都需要包含以下请求头：
```http
Content-Type: application/json
Cookie: t=your-token-here
```

### 3. 错误处理
| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查参数格式 |
| 401 | 未认证或认证失败 | 重新获取token |
| 403 | 无权限访问 | 检查权限设置 |
| 404 | 资源不存在 | 检查请求的ID |
| 500 | 服务器错误 | 稍后重试 |

### 4. 使用建议
1. 使用简化的任务操作方法
   - 通过项目名称而不是ID来操作任务
   - 使用标签名称直接管理任务标签
   - 批量操作提高效率

2. 数据处理最佳实践
   - 使用增量同步
   - 正确处理错误情况
   - 注意数据安全性

3. 性能优化
   - 合理使用批量操作
   - 适当的缓存策略
   - 控制请求频率

## 实用工具
1. [Apifox导入文件](apifox_import.json) - 用于在Apifox中测试API
2. [Postman集合](postman_collection.json) - 用于在Postman中测试API

## 常见问题
1. token获取失败
   - 检查账号密码是否正确
   - 确认是否有API访问权限

2. 请求返回401
   - token可能已过期
   - 需要重新登录获取token

3. 数据同步问题
   - 使用增量同步接口
   - 注意处理数据冲突

4. 批量操作限制
   - 单次请求数量限制
   - 请求频率限制

## 学习建议
1. 先阅读基础文档，了解API的基本使用
2. 通过实际示例学习具体应用
3. 循序渐进，从简单到复杂
4. 注意实践和错误处理

## 反馈与支持
如果你在学习过程中遇到问题，可以：
1. 查看[示例代码](../examples/)
2. 参考[字段说明](models/)
3. 提交Issue反馈问题 