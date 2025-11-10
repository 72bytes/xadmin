# 集成指南

## 路由配置

将以下路由配置添加到项目的路由文件中：

```typescript
// src/router/route.ts
{
  path: '/tpgen',
  name: 'TPGen',
  meta: {
    title: 'TPGen',
    icon: 'icon-experiment',
    order: 5,
  },
  children: [
    {
      path: 'online',
      name: 'TPGenOnline',
      component: () => import('@/views/tpgen/online/index.vue'),
      meta: {
        title: 'Test Plan Generator',
        icon: 'icon-experiment',
      },
    },
  ],
}
```

## 菜单配置

在数据库或配置文件中添加菜单项：

```sql
INSERT INTO system_menu (parent_id, name, path, component, icon, sort, type, status)
VALUES (NULL, 'TPGen', '/tpgen', 'Layout', 'icon-experiment', 5, 1, 1);

INSERT INTO system_menu (parent_id, name, path, component, icon, sort, type, status)
VALUES ((SELECT id FROM system_menu WHERE path = '/tpgen'), 'Test Plan Generator', '/tpgen/online', 'tpgen/online/index', 'icon-experiment', 1, 2, 1);
```

## 依赖安装

确保已安装必要的依赖：

```bash
# vue-draggable-plus 用于拖拽功能
pnpm add vue-draggable-plus
```

## API 配置

### 1. 创建 API 类型定义

在 `src/apis/test/type.ts` 中添加类型：

```typescript
// 机器信息
export interface Machine {
  id: number
  name: string
  motherboard: string
  gpu: string
  cpu: string
  status: 'Available' | 'Unavailable'
}

// 测试用例
export interface TestCase {
  id: number
  name: string
  description: string
  testType?: string
  subgroup?: string
}

// 生成测试计划请求
export interface GenerateTestPlanReq {
  cpu: string
  gpu: string
  machines: number[]
  osConfig: any
  kernelConfig: any
  firmwareVersion: string
  testCases: TestCase[]
}

// 生成测试计划响应
export interface GenerateTestPlanResp {
  yamlContent: string
  downloadUrl?: string
}
```

### 2. 创建 API 接口

在 `src/apis/test/plan.ts` 中添加接口：

```typescript
import type { GenerateTestPlanReq, GenerateTestPlanResp, Machine, TestCase } from './type'
import { request } from '@/utils/http'

/**
 * 获取机器列表
 */
export function getMachineList(params?: { cpu?: string; gpu?: string }) {
  return request<Machine[]>({
    url: '/test/machines',
    method: 'GET',
    params,
  })
}

/**
 * 获取测试用例列表
 */
export function getTestCaseList() {
  return request<TestCase[]>({
    url: '/test/cases',
    method: 'GET',
  })
}

/**
 * 生成测试计划
 */
export function generateTestPlan(data: GenerateTestPlanReq) {
  return request<GenerateTestPlanResp>({
    url: '/test/plan/generate',
    method: 'POST',
    data,
  })
}

/**
 * 上传并分析 YAML
 */
export function analyzeYaml(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/test/plan/analyze',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}
```

### 3. 在组件中使用 API

替换 Mock 数据调用为 API 调用：

```typescript
// 在 HardwareConfig.vue 中
import { getMachineList } from '@/apis/test/plan'

const { data: machines, loading } = await getMachineList({
  cpu: localCpu.value,
  gpu: localGpu.value,
})

// 在 CustomPlan.vue 中
import { generateTestPlan } from '@/apis/test/plan'

const handleGenerate = async () => {
  loading.value = true
  try {
    const { data } = await generateTestPlan(formData)
    generatedYaml.value = data
    Message.success('Test plan generated successfully')
  }
  catch (error) {
    Message.error('Failed to generate test plan')
  }
  finally {
    loading.value = false
  }
}
```

## 权限配置

如果需要权限控制，添加权限标识：

```typescript
// 在路由 meta 中添加
meta: {
  title: 'Test Plan Generator',
  icon: 'icon-experiment',
  permissions: ['test:plan:view', 'test:plan:generate'],
}

// 在组件中使用
<a-button v-permission="['test:plan:generate']" @click="handleGenerate">
  Generate Test Plan
</a-button>
```

## 样式定制

如果需要自定义主题颜色，修改 `index.scss` 中的 CSS 变量：

```scss
:root {
  --primary-color: #3498db;      // 主色
  --secondary-color: #2c3e50;    // 次要色
  --success-color: #27ae60;      // 成功色
  --warning-color: #f39c12;      // 警告色
  --danger-color: #e74c3c;       // 危险色
}
```

## 环境配置

在 `.env` 文件中添加相关配置：

```env
# 测试计划相关配置
VITE_API_TEST_PLAN_BASE_URL=/api/test
VITE_MAX_FILE_SIZE=10485760  # 10MB
```

## 测试

### 单元测试

```typescript
// tests/unit/tpgen/HardwareConfig.spec.ts
import { mount } from '@vue/test-utils'
import HardwareConfig from '@/views/tpgen/online/components/HardwareConfig.vue'

describe('HardwareConfig.vue', () => {
  it('renders correctly', () => {
    const wrapper = mount(HardwareConfig, {
      props: {
        cpu: 'Ryzen Threadripper',
        gpu: 'Radeon RX 7900 Series',
        selectedMachines: [],
      },
    })
    expect(wrapper.find('.section-title').text()).toContain('Hardware Platform Configuration')
  })

  it('filters machines correctly', async () => {
    const wrapper = mount(HardwareConfig, {
      props: {
        cpu: 'Ryzen Threadripper',
        gpu: 'Radeon RX 7900 Series',
        selectedMachines: [],
      },
    })
    // Add test logic
  })
})
```

## 部署注意事项

1. **文件上传大小限制**: 确保 Nginx 配置允许上传 YAML 文件
   ```nginx
   client_max_body_size 10M;
   ```

2. **YAML 文件验证**: 后端需要实现 YAML 格式验证

3. **安全性**: 
   - 文件类型检查
   - 文件大小限制
   - 内容安全扫描

4. **性能优化**:
   - 使用 CDN 加速静态资源
   - 启用 Gzip 压缩
   - 使用懒加载

## 常见问题

### Q: 拖拽功能不工作？
A: 确保安装了 `vue-draggable-plus` 依赖：
```bash
pnpm add vue-draggable-plus
```

### Q: 文件上传失败？
A: 检查：
1. 文件大小是否超过限制
2. 文件类型是否正确
3. 后端 API 是否正常

### Q: YAML 生成格式不正确？
A: 可以使用专业的 YAML 库如 `js-yaml`：
```bash
pnpm add js-yaml
pnpm add -D @types/js-yaml
```

然后在组件中使用：
```typescript
import yaml from 'js-yaml'

const yamlString = yaml.dump(yamlData)
```

## 支持

如有问题，请联系开发团队或查看项目文档。

