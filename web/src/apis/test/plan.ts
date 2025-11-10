import type * as T from "./type";
import http from "@/utils/http";

export type * from "./type";

const BASE_URL = "/system/test/plan";

/** @desc 查询测试计划列表 */
export function listTestPlan(query: T.TestPlanPageQuery) {
    return http.get<PageRes<T.TestPlanResp[]>>(`${BASE_URL}/list`, query);
}

/** @desc 查询测试计划详情 */
export function getTestPlan(id: string) {
    return http.get<T.TestPlanDetailResp>(`${BASE_URL}/${id}`);
}

/** @desc 新增测试计划 */
export function addTestPlan(data: T.TestPlanForm) {
    return http.post(`${BASE_URL}`, data);
}

/** @desc 修改测试计划 */
export function updateTestPlan(data: T.TestPlanForm, id: string) {
    return http.put(`${BASE_URL}/${id}`, data);
}

/** @desc 删除测试计划 */
export function deleteTestPlan(ids: string | Array<string>) {
    return http.del(`${BASE_URL}/${ids}`);
}

