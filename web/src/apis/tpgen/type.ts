export interface SavedPlanResp {
  id: string
  name: string
  category: string
  description: string
  configData: any
  yamlData?: any
  cpu?: string
  gpu?: string
  machineCount: number
  osType?: string
  kernelType?: string
  testCaseCount: number
  status: number
  tags?: string
  useCount: number
  lastUsedTime?: string
  createUser: number
  createUserString: string
  createTime: string
  updateUser?: number
  updateUserString?: string
  updateTime?: string
}

export interface SavedPlanDetailResp extends SavedPlanResp {
  configData: any
  yamlData?: any
}

export interface SavedPlanQuery {
  name?: string
  category?: string
  createUser?: number
  status?: number
}

export interface SavedPlanPageQuery extends SavedPlanQuery {
  page?: number
  size?: number
  sort?: string[]
}

export interface SavedPlanForm {
  name: string
  category: string
  description?: string
  configData: any
  yamlData?: any
  cpu?: string
  gpu?: string
  machineCount: number
  osType?: string
  kernelType?: string
  testCaseCount: number
  status: number
  tags?: string
}
