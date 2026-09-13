import Taro from '@tarojs/taro'

const HISTORY_KEY = 'bea_history'
const MAX_HISTORY = 20

/**
 * 保存分析结果到本地历史
 */
export function saveToHistory(result) {
  try {
    let history = Taro.getStorageSync(HISTORY_KEY)
    if (!history) history = []

    history.unshift({
      id: result.history_id || Date.now().toString(),
      timestamp: new Date().toISOString(),
      image_url: result.image_url,
      paradigm: result.paradigm?.name,
      wt: result.wt,
      total_score: result.total_score,
      result: result
    })

    // 只保留最近 N 条
    history = history.slice(0, MAX_HISTORY)
    Taro.setStorageSync(HISTORY_KEY, history)
    return true
  } catch (e) {
    console.error('保存历史失败:', e)
    return false
  }
}

/**
 * 获取本地历史记录
 */
export function getLocalHistory() {
  try {
    const history = Taro.getStorageSync(HISTORY_KEY)
    return history || []
  } catch (e) {
    return []
  }
}

/**
 * 清空历史记录
 */
export function clearHistory() {
  try {
    Taro.removeStorageSync(HISTORY_KEY)
    return true
  } catch (e) {
    return false
  }
}

/**
 * 保存当前分析结果（用于报告页读取）
 */
export function saveCurrentResult(result) {
  try {
    Taro.setStorageSync('bea_current_result', result)
    return true
  } catch (e) {
    return false
  }
}

/**
 * 获取当前分析结果
 */
export function getCurrentResult() {
  try {
    return Taro.getStorageSync('bea_current_result')
  } catch (e) {
    return null
  }
}

/**
 * 清除当前分析结果
 */
export function clearCurrentResult() {
  try {
    Taro.removeStorageSync('bea_current_result')
    return true
  } catch (e) {
    return false
  }
}

export default {
  saveToHistory,
  getLocalHistory,
  clearHistory,
  saveCurrentResult,
  getCurrentResult,
  clearCurrentResult
}
