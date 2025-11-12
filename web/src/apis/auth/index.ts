import type * as T from './type'
import http from '@/utils/http'

export type * from './type'

const BASE_URL = '/system/auth'

/** @desc 账号登录 */
export function accountLogin(req: T.AccountLoginReq) {
  return http.post<T.LoginResp>(`${BASE_URL}/login`, req)
}

/** @desc 手机号登录 */
export function phoneLogin(req: T.PhoneLoginReq) {
  return http.post<T.LoginResp>(`${BASE_URL}/phone`, req)
}

/** @desc 邮箱登录 */
export function emailLogin(req: T.EmailLoginReq) {
  return http.post<T.LoginResp>(`${BASE_URL}/email`, req)
}

// 第三方账号功能已删除 - 保留空函数以避免构建错误
/** @desc 三方账号登录 */
export function socialLogin(source: string, req: any) {
  return Promise.reject(new Error('Social account feature is disabled'))
}

/** @desc 三方账号登录授权 */
export function socialAuth(source: string) {
  return Promise.reject(new Error('Social account feature is disabled'))
}

/** @desc 退出登录 */
export function logout() {
  return http.post(`${BASE_URL}/logout`)
}

/** @desc 获取用户信息 */
export const getUserInfo = () => {
  return http.get<T.UserInfo>(`${BASE_URL}/user/info`)
}

/** @desc 获取路由信息 */
export const getUserRoute = () => {
  return http.get<T.RouteItem[]>(`${BASE_URL}/route`)
}
