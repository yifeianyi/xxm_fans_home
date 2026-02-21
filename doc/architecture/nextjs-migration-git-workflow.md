# Next.js 改造 Git 工作流指南

> 版本：v1.0  
> 创建日期：2026-02-18  
> 适用场景：小满虫之家前端迁移至 Next.js

---

## 📌 概述

将现有 Vite + React 项目迁移至 Next.js 15 + App Router，采用与原项目一致的**多段独立历史**管理模式。

### 原项目的历史模式

```
* 4ef92d0 (HEAD -> main) 当前 React 版本
...
* 07161ae first commit  ← root commit（没有 parent）

* a0ed6a2 (tag: legacy-vue-last) Vue 版本  ← 另一个 root commit
...
```

**特征**：多个独立的 root commit 通过 merge 共存，工作目录为最新代码，但可通过 `git checkout` 查看历史版本。

### 本次迁移目标

创建**第三段独立历史**（Next.js），最终形成：
- 三个 root commit 并存（Vue、React、Next.js）
- 通过 merge commit 连接
- 工作目录为 Next.js 代码
- 保留完整的开发历史

---

## 🔄 工作流程

```
Phase 1: 独立开发（repo/xxm_nextjs/）
┌─────────────────────────────────────────────┐
│  * abc1234 (HEAD, tag: v1.0.0-ready)        │
│  * ...                                      │
│  * def5678 init: initialize Next.js         │
│         ↑                                   │
│    root commit（无 parent）                  │
└─────────────────────────────────────────────┘
                    │
                    │ 步骤 1: 创建孤儿分支（--orphan）
                    │ 步骤 2: 删除原分支所有文件
                    │ 步骤 3: pull 新项目内容
                    ▼
Phase 2: 在干净分支中获取新项目
┌─────────────────────────────────────────────┐
│  分支: nextjs-clean（完全干净）               │
│  * abc1234 (tag: v1.0.0-ready)              │
│  * ...                                      │
│  * def5678 init: initialize Next.js         │
│  （没有任何原项目的文件，连.gitignore都没有）  │
└─────────────────────────────────────────────┘
                    │
                    │ git merge --allow-unrelated-histories
                    ▼
Phase 3: 合并到 main
┌─────────────────────────────────────────────────────────────┐
│  * xyz7890 (HEAD -> main, tag: v3.0.0) Merge branch 'nextjs-clean'│
│  |\                                                          │
│  | * abc1234 (tag: nextjs-root) Next.js 最新提交             │
│  | * def5678 init: initialize Next.js（root commit）         │
│  |                                                          │
│  * 4ef92d0 React 最新提交                                    │
│  * 07161ae React root commit                                 │
│  * a0ed6a2 (tag: legacy-vue-last) Vue root commit            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 创建独立开发目录

```bash
mkdir -p repo/xxm_nextjs
cd repo/xxm_nextjs

# 初始化全新 Git 仓库
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 注意：本项目仅在本地开发，不需要添加远程仓库
```

### 2. 初始化 Next.js 项目

```bash
npx create-next-app@latest . \
  --typescript --tailwind --eslint --app \
  --src-dir=false --import-alias="@/*" --use-npm

npm run dev
```

### 3. 开发并提交

```bash
# 正常开发，正常提交
git add -A
git commit -m "init: initialize Next.js project"

# ... 开发更多功能 ...
git commit -m "feat: migrate home page"

# 推送备份
git push origin main
```

---

## 🔗 合并到原项目

### 方案：创建孤儿分支（干净的分支）

创建一个**完全干净**的分支，只有新项目的代码，没有任何原项目的文件（包括 `.gitignore`）。

```bash
# 进入原项目
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend

# 确认当前有两个 root commit
git rev-list --max-parents=0 --all

# 添加 Next.js 项目作为远程
git remote add nextjs /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_nextjs
git fetch nextjs

# 1. 创建孤儿分支（没有 parent，完全干净）
git checkout --orphan nextjs-clean

# 2. 删除所有文件（保留 .git 目录）
git rm -rf .

# 3. 拉取新项目内容（此时分支是空的，只有新项目）
git pull /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_nextjs main --allow-unrelated-histories

# 现在 nextjs-clean 分支只有 Next.js 的内容，没有原项目的任何文件
# 连 .gitignore 都是 Next.js 项目的

# 4. 添加里程碑标签
git tag -a nextjs-root -m "Next.js era begins (third root commit, clean branch)"
git tag -a v3.0.0 -m "Next.js migration complete"

# 5. 将干净分支合并到 main
git checkout main
git merge nextjs-clean --allow-unrelated-histories -m "feat: merge Next.js migration

Merge independent Next.js development history (clean branch) into main project.
This creates a third root commit alongside Vue and React histories.

Phase completion:
- v0.1.0-init: Environment setup
- v0.2.0-foundation: Foundation architecture
- v0.3.0-static-pages: Static pages migration
- v0.4.0-data-pages: Data-driven pages
- v0.5.0-complex-pages: Complex pages
- v1.0.0-ready: Optimization complete

Work directory now contains Next.js code."

# 6. 推送
git push origin main --tags

# 7. 清理（可选：保留或删除干净分支）
git remote remove nextjs
# git branch -d nextjs-clean  # 可选：删除干净分支，或保留作为归档
```

### 验证合并结果

```bash
# 查看分叉历史
git log --oneline --graph --all -20

# 确认三个 root commit
git rev-list --max-parents=0 --all
# 应输出：
# a0ed6a2... (Vue)
# 07161ae... (React)
# def5678... (Next.js)

# 确认无共同祖先
git merge-base 07161ae a0ed6a2      # 报错
git merge-base def5678 07161ae       # 报错
```

---

## 📂 工作目录与历史查看

### 当前工作目录（Next.js）

```bash
$ ls -la
app/              # Next.js App Router
components/       # React 组件
lib/              # 工具函数
next.config.ts    # Next.js 配置
...

# 原 React 的 src/ 被覆盖，但历史中保留
```

### 查看历史版本

```bash
# 查看 React 版本
git checkout 07161ae
ls -la  # 会看到 src/ 目录（React 代码）

# 查看 Vue 版本
git checkout a0ed6a2
ls -la  # 会看到 Vue 的文件结构

# 回到最新
git checkout main
```

---

## ❓ 常见问题

### Q1: 如何只保留代码，不保留独立开发的历史？

```bash
# 文件复制方案（简单直接，无独立历史）
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend

git rm -rf src/ vite.config.* index.html
cp -r /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_nextjs/* .
git add -A
git commit -m "feat: migrate to Next.js (files only)"
```

### Q2: Merge 出错如何回滚？

```bash
git checkout main
git reset --hard origin/main  # 回到 merge 前状态
# 修复问题后重新 merge
```

### Q3: 独立开发期间如何参考原项目代码？

```bash
# 终端 1：开发新项目
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_nextjs
npm run dev

# 终端 2：查看原项目代码
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend
# 查看文件、对比实现...
```

---

**最后更新**：2026-02-18  
**状态**：📋 准备就绪
