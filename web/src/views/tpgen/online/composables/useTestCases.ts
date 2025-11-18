/**
 * 测试用例数据管理 Composable
 * 统一管理从数据库获取的真实测试用例数据
 */

import { computed, ref } from 'vue'
import type { TestCase, TestCaseGroup } from '../types'
import * as tpdbApi from '@/apis/tpdb'
import { showNotification } from '../check_yaml'

// 全局测试用例数据缓存
const testCaseGroupsCache = ref<TestCaseGroup>({})
const loading = ref(false)
const loaded = ref(false)

export function useTestCases() {
  /**
   * 加载测试用例数据
   * 从数据库获取完整的测试用例树形结构
   */
  const loadTestCases = async (force = false) => {
    // 如果已加载且不是强制刷新，直接返回缓存
    if (loaded.value && !force) {
      return testCaseGroupsCache.value
    }

    loading.value = true
    try {
      // 获取所有测试类型
      const typesResponse = await tpdbApi.listTestTypes()
      if (!typesResponse.success || !typesResponse.data) {
        throw new Error('获取测试类型失败')
      }

      const types = typesResponse.data
      const groups: TestCaseGroup = {}

      // 为每个测试类型获取组件和用例
      for (const type of types) {
        const typeName = type.typeName
        groups[typeName] = {}

        // 获取该测试类型的所有组件
        const componentsResponse = await tpdbApi.listTestComponents({ test_type_id: type.id })
        if (componentsResponse.success && componentsResponse.data) {
          const components = componentsResponse.data

          // 为每个组件获取测试用例
          for (const component of components) {
            const componentKey = component.componentName
            groups[typeName][componentKey] = []

            // 获取该组件的所有测试用例
            const casesResponse = await tpdbApi.listTestCases({
              test_component_id: component.id,
              page: 1,
              size: 1000,
            })

            if (casesResponse.success && casesResponse.data?.list) {
              // 转换数据格式
              groups[typeName][componentKey] = casesResponse.data.list.map((tc) => ({
                id: tc.id,
                caseName: tc.caseName,
                caseConfig: tc.caseConfig,
                testComponentId: tc.testComponentId,
                // 兼容旧字段
                name: tc.caseName,
                description: tc.caseConfig?.description || '',
                testType: typeName,
                testTypeName: typeName,
                componentName: component.componentName,
                componentCategory: component.componentCategory,
                subgroup: component.componentName,
              }))
            }
          }
        }
      }

      testCaseGroupsCache.value = groups
      loaded.value = true
      console.log('[useTestCases] 测试用例数据加载成功:', groups)
      return groups
    } catch (error) {
      console.error('[useTestCases] 加载测试用例失败:', error)
      showNotification('加载测试用例数据失败', 'error')
      return {}
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取所有测试用例（扁平化）
   */
  const getAllTestCases = computed(() => {
    const allCases: TestCase[] = []
    Object.entries(testCaseGroupsCache.value).forEach(([testType, subgroups]) => {
      Object.entries(subgroups).forEach(([subgroup, cases]) => {
        allCases.push(...cases)
      })
    })
    return allCases
  })

  /**
   * 按测试类型获取用例
   */
  const getTestCasesByType = (testType: string): TestCase[] => {
    const allCases: TestCase[] = []
    const subgroups = testCaseGroupsCache.value[testType]
    if (subgroups) {
      Object.values(subgroups).forEach((cases) => {
        allCases.push(...cases)
      })
    }
    return allCases
  }

  /**
   * 按组件获取用例
   */
  const getTestCasesByComponent = (testType: string, componentName: string): TestCase[] => {
    return testCaseGroupsCache.value[testType]?.[componentName] || []
  }

  /**
   * 搜索测试用例
   */
  const searchTestCases = (keyword: string): TestCase[] => {
    if (!keyword) return getAllTestCases.value

    const lowerKeyword = keyword.toLowerCase()
    return getAllTestCases.value.filter((tc) =>
      tc.caseName?.toLowerCase().includes(lowerKeyword)
      || tc.name?.toLowerCase().includes(lowerKeyword)
      || tc.description?.toLowerCase().includes(lowerKeyword)
      || tc.componentName?.toLowerCase().includes(lowerKeyword),
    )
  }

  return {
    testCaseGroups: computed(() => testCaseGroupsCache.value),
    loading: computed(() => loading.value),
    loaded: computed(() => loaded.value),
    loadTestCases,
    getAllTestCases,
    getTestCasesByType,
    getTestCasesByComponent,
    searchTestCases,
  }
}
