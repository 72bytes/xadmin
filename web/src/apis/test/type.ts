export interface TestPlanResp {
  id: string
  name: string
  code: string
  description: string
  startTime: string
  endTime: string
  ownerId: number | null
  ownerName: string
  priority: number
  status: number
  testType: string
  testEnv: string
  relatedProject: string
  remark: string
  createUser: number
  createUserString: string
  createTime: string
  updateUser: number | null
  updateUserString: string
  updateTime: string
}

export interface TestPlanDetailResp {
  id: string
  name: string
  code: string
  description: string
  startTime: string
  endTime: string
  ownerId: number | null
  ownerName: string
  priority: number
  status: number
  testType: string
  testEnv: string
  relatedProject: string
  remark: string
  createUser: number
  createUserString: string
  createTime: string
  updateUser: number | null
  updateUserString: string
  updateTime: string
}

export interface TestPlanQuery {
  name?: string
  code?: string
  status?: number
  priority?: number
}

export interface TestPlanPageQuery extends TestPlanQuery {
  page?: number
  size?: number
  sort?: string[]
}

export interface TestPlanForm {
  name: string
  code: string
  description?: string
  startTime?: string
  endTime?: string
  ownerId?: number
  ownerName?: string
  priority: number
  status: number
  testType?: string
  testEnv?: string
  relatedProject?: string
  remark?: string
}

