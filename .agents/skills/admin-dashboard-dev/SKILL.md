---
name: admin-dashboard-dev
description: XXM Fans Admin 后台管理系统开发工作流 - 页面开发、API对接、组件开发、表单开发、数据可视化
---

# Admin Dashboard Dev - 后台开发工作流

本 Skill 提供 XXM Fans Admin 后台管理系统的完整开发工作流，涵盖页面开发、API 对接、组件封装、表单处理、数据可视化等场景。

%% AGENT FLOW
BEGIN -> select_workflow -> execute_workflow -> END

select_workflow:
  task: 选择后台开发工作流
  description: 根据用户当前的后台开发任务选择合适的工作流
  branches:
    - condition: 用户需要开发新页面
      next: page-development
    - condition: 用户需要对接后端 API
      next: api-integration
    - condition: 用户需要开发通用组件
      next: component-development
    - condition: 用户需要开发表单功能
      next: form-development
    - condition: 用户需要添加数据可视化/图表
      next: chart-development
    - condition: 用户需要完善权限控制
      next: permission-development
    - condition: 用户需要优化性能
      next: performance-optimization

execute_workflow:
  task: 执行选定的工作流
  description: 加载对应的工作流 YAML 文件并执行
%%

## 项目架构回顾

```
xxm_fans_admin/
├── src/
│   ├── domain/           # 领域层 - 类型定义、服务接口
│   │   ├── types/
│   │   └── api/
│   ├── infrastructure/   # 基础设施层 - API实现、配置
│   │   ├── api/
│   │   └── config/
│   ├── presentation/     # 表现层 - 组件、页面
│   │   ├── components/
│   │   └── pages/
│   ├── shared/          # 共享层 - 工具函数、Hooks
│   ├── stores/          # 状态管理
│   └── router/          # 路由配置
```

## 可用工作流

| 工作流 | 文件 | 适用场景 |
|--------|------|----------|
| **page-development** | `workflows/page-development.yml` | 新页面开发（列表页、详情页、表单页） |
| **api-integration** | `workflows/api-integration.yml` | 对接后端 API、实现 Service |
| **component-development** | `workflows/component-development.yml` | 开发通用组件（表格、表单、弹窗等） |
| **form-development** | `workflows/form-development.yml` | 表单开发（校验、动态表单、复杂表单） |
| **chart-development** | `workflows/chart-development.yml` | 数据可视化、ECharts 图表开发 |
| **permission-development** | `workflows/permission-development.yml` | 权限控制、菜单权限、按钮权限 |
| **performance-optimization** | `workflows/performance-optimization.yml` | 性能优化（列表虚拟滚动、懒加载等） |

## 技术栈

- **框架**: React 18 + TypeScript 5.8
- **构建**: Vite 6
- **UI库**: Ant Design 5.x
- **状态**: Zustand 5
- **图表**: ECharts + echarts-for-react
- **架构**: DDD（领域驱动设计）

## 目录规范

### 新增页面
```
src/presentation/pages/PageName/
├── index.tsx           # 页面入口
├── components/         # 页面专属组件
├── hooks/             # 页面专属 Hooks
└── styles/            # 页面样式（如需要）
```

### 新增组件
```
src/presentation/components/
├── common/            # 通用组件（Loading、ErrorBoundary等）
├── forms/             # 表单组件
├── tables/            # 表格组件
└── charts/            # 图表组件
```

### 新增 API 服务
```
src/infrastructure/api/
├── xxxService.ts      # 服务实现
└── index.ts          # 导出

src/domain/api/
├── IXxxService.ts     # 服务接口
└── index.ts          # 导出
```

## 使用方式

### 开发新页面
```
用户：帮我开发一个歌曲分类管理页面
→ 读取 workflows/page-development.yml
→ 按照步骤创建页面
```

### 对接 API
```
用户：后端已经提供了API，帮我对接一下
→ 读取 workflows/api-integration.yml
→ 创建 Service 接口和实现
```

### 开发组件
```
用户：需要一个可以批量编辑的表格组件
→ 读取 workflows/component-development.yml
→ 开发通用表格组件
```

## 快速检查清单

开发完成后，检查以下事项：

- [ ] 类型定义完整（domain/types）
- [ ] 服务接口定义（domain/api）
- [ ] 服务实现完成（infrastructure/api）
- [ ] 页面组件实现（presentation/pages）
- [ ] 路由配置添加（router/index.tsx）
- [ ] 菜单配置添加（infrastructure/config/config.ts）
- [ ] 权限控制实现（如需要）
- [ ] 错误处理完善
- [ ] 加载状态处理
- [ ] 空状态处理

## 最佳实践

1. **严格遵循 DDD 分层**: Domain → Infrastructure → Presentation
2. **优先定义类型**: 先定义 domain/types，再实现功能
3. **接口与实现分离**: domain/api 定义接口，infrastructure/api 实现
4. **组件原子化**: 复杂组件拆分为小组件
5. **状态管理**: 全局状态用 Zustand，本地状态用 useState
6. **错误处理**: 统一在 httpClient 拦截器处理，页面捕获具体错误
7. **类型安全**: 所有函数返回值必须声明类型

## 常见开发模式

### 列表页开发模式
```typescript
// 1. 定义筛选类型
type Filter = { keyword?: string; status?: string };

// 2. 页面状态
const [filter, setFilter] = useState<Filter>({});
const [pagination, setPagination] = useState({ page: 1, pageSize: 20 });
const [data, setData] = useState<Item[]>([]);
const [loading, setLoading] = useState(false);

// 3. 数据获取
const fetchData = useCallback(async () => {
  setLoading(true);
  try {
    const result = await xxxService.getList(filter, pagination);
    setData(result.data.items);
  } finally {
    setLoading(false);
  }
}, [filter, pagination]);

// 4. useEffect 触发
useEffect(() => { fetchData(); }, [fetchData]);
```

### 表单页开发模式
```typescript
// 1. 定义表单类型
type FormValues = { name: string; description?: string };

// 2. 使用 Antd Form
const [form] = Form.useForm<FormValues>();

// 3. 提交处理
const handleSubmit = async (values: FormValues) => {
  try {
    if (isEdit) {
      await xxxService.update(id, values);
    } else {
      await xxxService.create(values);
    }
    message.success('保存成功');
    navigate('/xxx');
  } catch (error) {
    message.error(error.message);
  }
};
```
