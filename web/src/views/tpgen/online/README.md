# TPGen - Test Plan Generator

一个现代化的测试计划生成器，基于 Vue 3 + TypeScript + Arco Design 构建。

## 功能特性

### 1. 上传测试计划
- 支持拖拽上传 YAML 文件
- 自动解析和验证 YAML 配置
- 智能分析机器兼容性
- 详细的分析报告展示

### 2. 自定义测试计划
- **硬件平台配置**
  - CPU 型号选择
  - GPU 产品线选择
  - 可视化机器列表选择
  - 自动过滤兼容机器

- **操作系统环境**
  - 统一配置模式
  - 独立配置模式（每台机器单独配置）
  - 支持多种 Linux 发行版
  - 部署方式选择（裸机/虚拟机/容器）

- **内核和驱动配置**
  - 统一/独立配置模式
  - 内核类型选择
  - 内核版本选择

- **固件管理**
  - GPU 固件版本选择
  - 版本比较测试选项

- **测试用例管理**
  - 预定义测试用例组（Benchmark, Functional, Performance, Stress）
  - 测试用例搜索功能
  - 拖拽排序支持
  - 自定义测试组创建
  - 实时预览选中的测试用例

### 3. YAML 生成
- 自动生成标准 YAML 格式
- 代码高亮显示
- 一键复制到剪贴板
- 下载为文件

### 4. 其他特性
- 实时进度跟踪
- 响应式设计，支持移动端
- 流畅的动画效果
- 友好的用户交互体验

## 项目结构

```
src/views/tpgen/online/
├── index.vue                      # 主入口页面
├── index.scss                     # 全局样式
├── types.ts                       # TypeScript 类型定义
├── mockData.ts                    # Mock 数据和选项配置
├── README.md                      # 项目文档
└── components/                    # 组件目录
    ├── UploadPlan.vue            # 上传测试计划组件
    ├── CustomPlan.vue            # 自定义测试计划组件
    ├── HardwareConfig.vue        # 硬件平台配置组件
    ├── OSConfig.vue              # 操作系统配置组件
    ├── KernelConfig.vue          # 内核配置组件
    ├── FirmwareConfig.vue        # 固件配置组件
    ├── TestCaseManager.vue       # 测试用例管理组件
    ├── CustomGroupModal.vue      # 自定义组模态框组件
    └── YamlPreview.vue           # YAML 预览组件
```

## 组件说明

### 核心组件

#### `index.vue`
主入口组件，包含：
- Tab 切换（上传/自定义）
- 进度显示
- 整体布局

#### `UploadPlan.vue`
上传测试计划功能：
- 文件上传（支持拖拽）
- YAML 解析
- 兼容性分析
- 分析结果展示

#### `CustomPlan.vue`
自定义测试计划核心组件：
- 表单管理
- 进度计算
- YAML 生成
- 子组件集成

### 配置组件

#### `HardwareConfig.vue`
硬件平台配置：
- CPU/GPU 选择
- 机器列表展示
- 机器选择管理
- 自动过滤

#### `OSConfig.vue`
操作系统配置：
- 配置模式切换
- 统一配置
- 独立配置
- 动态表单生成

#### `KernelConfig.vue`
内核配置：
- 配置模式切换
- 内核类型/版本选择
- 独立机器配置

#### `FirmwareConfig.vue`
固件配置：
- 固件版本选择
- 版本比较选项

### 测试用例组件

#### `TestCaseManager.vue`
测试用例管理器：
- 测试用例组展示
- 搜索功能
- 复选框选择
- 拖拽排序
- 自定义组管理

#### `CustomGroupModal.vue`
自定义组模态框：
- 组名输入
- 现有用例选择
- 新用例创建
- 已选用例预览

#### `YamlPreview.vue`
YAML 预览组件：
- YAML 格式化显示
- 复制到剪贴板
- 下载文件

## 数据流

```
index.vue
  ├─> UploadPlan.vue (独立功能)
  └─> CustomPlan.vue
        ├─> HardwareConfig.vue ──┐
        ├─> OSConfig.vue ────────┤
        ├─> KernelConfig.vue ────┤──> emit('update') ──> updateProgress()
        ├─> FirmwareConfig.vue ──┤
        └─> TestCaseManager.vue ─┘
              └─> CustomGroupModal.vue
```

## Mock 数据

所有 Mock 数据定义在 `mockData.ts` 中，包括：
- 机器列表 (`mockMachines`)
- 测试用例组 (`testCaseGroups`)
- CPU 选项 (`cpuOptions`)
- GPU 选项 (`gpuOptions`)
- OS 选项 (`osOptions`)
- 部署方式选项 (`deploymentOptions`)
- 内核类型选项 (`kernelTypeOptions`)
- 内核版本选项 (`kernelVersionOptions`)
- 固件版本选项 (`firmwareVersionOptions`)

在实际项目中，这些数据应该从后端 API 获取。

## 技术栈

- **Vue 3**: 使用 Composition API
- **TypeScript**: 完整的类型支持
- **Arco Design**: UI 组件库
- **vue-draggable-plus**: 拖拽功能
- **SCSS**: 样式预处理器

## 开发指南

### 添加新的测试用例组

1. 在 `mockData.ts` 中的 `testCaseGroups` 添加新组
2. 组件会自动渲染新的测试用例组

### 添加新的配置选项

1. 在 `mockData.ts` 中添加新选项
2. 在相应的配置组件中使用

### 自定义样式

所有组件都使用 scoped 样式，可以直接修改各组件的 `<style>` 部分。

全局样式定义在 `index.scss` 中。

## API 集成

当前使用 Mock 数据，实际项目中需要：

1. 在 `src/apis/test/plan.ts` 中定义 API 接口
2. 在组件中替换 Mock 数据调用为 API 调用
3. 添加 loading 状态管理
4. 添加错误处理

示例：

```typescript
// 获取机器列表
const { data: machines, loading } = await getMachines({
  cpu: formData.cpu,
  gpu: formData.gpu
})

// 生成测试计划
const result = await generateTestPlan(formData)
```

## 性能优化

- 使用 `computed` 进行数据计算缓存
- 大列表使用虚拟滚动（可选）
- 防抖搜索输入
- 懒加载组件（可选）

## 注意事项

1. **表单验证**: 当前为基础验证，可根据需要增强
2. **本地存储**: 可以添加 localStorage 保存用户配置
3. **权限控制**: 可以集成项目的权限系统
4. **国际化**: 可以添加 i18n 支持

## 后续优化建议

1. 添加表单校验规则
2. 添加本地存储功能
3. 集成真实 API
4. 添加更多测试用例类型
5. 添加测试计划模板功能
6. 添加历史记录功能
7. 优化移动端体验
8. 添加导出其他格式（JSON, XML 等）

## License

MIT

