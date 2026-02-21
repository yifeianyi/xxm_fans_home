---
name: workflow
description: XXM Fans Home 项目开发工作流集合 - 新功能开发、Bug修复、API开发、UI修改、版本发布、Next.js迁移
---

# Workflow 工作流集合

本 Skill 整合了 XXM Fans Home 项目的所有开发工作流。

%% AGENT FLOW
BEGIN -> select_workflow -> execute_workflow -> END

select_workflow:
  task: 选择工作流
  description: 根据用户需求选择合适的开发工作流
  branches:
    - condition: 用户需要开发新功能（前后端都涉及）
      next: feature-dev
    - condition: 用户需要修复 Bug
      next: bug-fix
    - condition: 用户需要开发后端 API
      next: api-development
    - condition: 用户需要修改前端 UI
      next: frontend-ui-update
    - condition: 用户需要发布版本
      next: release
    - condition: 用户在进行 Next.js 迁移
      next: nextjs-migration

execute_workflow:
  task: 执行选定的工作流
  description: 加载对应的工作流 YAML 文件并执行
%%

## 可用工作流

| 工作流 | 文件 | 适用场景 |
|--------|------|----------|
| **feature-dev** | `workflows/feature-dev.yml` | 新功能开发（支持跨前后端协作） |
| **bug-fix** | `workflows/bug-fix.yml` | Bug 修复（支持热修复和常规修复） |
| **api-development** | `workflows/api-development.yml` | 后端 API 开发专用流程 |
| **frontend-ui-update** | `workflows/frontend-ui-update.yml` | 前端 UI 修改流程 |
| **release** | `workflows/release.yml` | 版本发布流程 |
| **nextjs-migration** | `workflows/nextjs-migration.yml` | Next.js 迁移项目开发流程 |

## 使用方法

1. 询问用户当前的任务类型
2. 根据任务类型选择对应的工作流
3. 使用 ReadFile 读取对应的 YAML 文件内容
4. 按照 YAML 中的步骤逐步执行

## 工作流文件位置

所有工作流文件位于本 skill 的 `workflows/` 目录下：
- `workflows/feature-dev.yml`
- `workflows/bug-fix.yml`
- `workflows/api-development.yml`
- `workflows/frontend-ui-update.yml`
- `workflows/release.yml`
- `workflows/nextjs-migration.yml`

---

## select_workflow

请根据用户的需求，询问以下问题：

1. **当前的任务类型是什么？**
   - 开发新功能
   - 修复 Bug
   - 开发后端 API
   - 修改前端 UI
   - 发布版本
   - Next.js 迁移

2. **涉及哪些模块？**（后端/前端/两者）

3. **是否有紧急程度要求？**（如热修复）

根据用户的回答，选择对应的工作流，然后读取相应的 YAML 文件执行。

---

## execute_workflow

加载选定的工作流文件，按照其中的 `steps` 逐步执行：

1. 使用 `ReadFile` 读取 `workflows/<workflow-name>.yml`
2. 解析 YAML 中的步骤定义
3. 按顺序执行每个步骤（注意处理 `condition` 条件）
4. 每个步骤完成后，询问用户是否继续下一步

工作流执行完成后，输出完成总结。
