import Taro from '@tarojs/taro'

// API 基础地址（可通过环境变量配置）
const BASE_URL = process.env.API_BASE_URL || 'https://api.bea-aesthetics.com'

/**
 * 通用请求封装
 */
function request(options) {
  return new Promise((resolve, reject) => {
    Taro.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(new Error(`请求失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

/**
 * 图片分析 API
 * @param {string} filePath - 图片临时路径
 * @returns {Promise} 分析结果
 */
export function analyzeImage(filePath) {
  return new Promise((resolve, reject) => {
    Taro.uploadFile({
      url: BASE_URL + '/api/analyze',
      filePath: filePath,
      name: 'image',
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          if (res.statusCode === 200) {
            resolve(data)
          } else {
            reject(new Error(data.error || '分析失败'))
          }
        } catch (e) {
          reject(new Error('响应解析失败'))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

/**
 * 健康检查
 */
export function healthCheck() {
  return request({
    url: '/api/health',
    method: 'GET'
  })
}

/**
 * 获取历史记录
 */
export function getHistory() {
  return request({
    url: '/api/history',
    method: 'GET'
  })
}

/**
 * 获取历史详情
 */
export function getHistoryDetail(id) {
  return request({
    url: `/api/history/${id}`,
    method: 'GET'
  })
}

export default {
  analyzeImage,
  healthCheck,
  getHistory,
  getHistoryDetail
}
