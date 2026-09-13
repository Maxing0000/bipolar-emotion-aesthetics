import { Component } from 'react'
import { View, Text, Image, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { analyzeImage } from '../../utils/api'
import { saveToHistory, saveCurrentResult, getLocalHistory } from '../../utils/storage'
import './index.scss'

// 精选案例
const FEATURED_CASES = [
  { name: 'iPhone 17 Pro', paradigm: '崇高震撼', score: 86, image: 'https://maxing0000.github.io/bipolar-emotion-aesthetics/cases/images/01-iphone17-pro.jpg' },
  { name: '尊界 S800', paradigm: '崇高震撼', score: 94, image: 'https://maxing0000.github.io/bipolar-emotion-aesthetics/cases/images/02-zunjie-s800.jpg' },
  { name: '小米 SU7', paradigm: '冷峻克制', score: 84, image: 'https://maxing0000.github.io/bipolar-emotion-aesthetics/cases/images/03-xiaomi-su7.jpg' },
  { name: '奔驰 S 级', paradigm: '均衡典雅', score: 89, image: 'https://maxing0000.github.io/bipolar-emotion-aesthetics/cases/images/07-mercedes-s-class.jpg' },
]

export default class Index extends Component {
  config = {
    navigationBarTitleText: 'BEA 美学分析'
  }

  constructor(props) {
    super(props)
    this.state = {
      history: [],
      analyzing: false
    }
  }

  componentDidMount() {
    this.loadHistory()
  }

  componentDidShow() {
    this.loadHistory()
  }

  // 加载历史记录
  loadHistory() {
    const history = getLocalHistory()
    this.setState({ history })
  }

  // 选择图片
  chooseImage(sourceType) {
    if (this.state.analyzing) return

    Taro.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: sourceType || ['album', 'camera'],
      success: (res) => {
        const filePath = res.tempFilePaths[0]
        this.startAnalyze(filePath)
      },
      fail: (err) => {
        if (err.errMsg && err.errMsg.indexOf('cancel') === -1) {
          Taro.showToast({ title: '选择图片失败', icon: 'none' })
        }
      }
    })
  }

  // 开始分析
  async startAnalyze(filePath) {
    this.setState({ analyzing: true })

    // 跳转到分析中页面，传递图片路径
    Taro.navigateTo({
      url: `/pages/analyze/analyze?filePath=${encodeURIComponent(filePath)}`
    })

    this.setState({ analyzing: false })
  }

  // 查看历史详情
  viewHistory(item) {
    saveCurrentResult(item.result)
    Taro.navigateTo({ url: '/pages/report/report' })
  }

  render() {
    const { history } = this.state

    return (
      <View className='index-page'>
        {/* 头部 */}
        <View className='home-header'>
          <View className='bea-logo'>B</View>
          <Text className='home-title'>双极情绪美学</Text>
          <Text className='home-desc'>拍一张照片，30秒看懂为什么美</Text>
        </View>

        {/* 拍照区域 */}
        <View className='capture-section'>
          <View className='capture-btn' onClick={this.chooseImage.bind(this, ['album', 'camera'])}>
            <Text className='capture-icon'>📸</Text>
            <Text className='capture-title'>拍照分析</Text>
            <Text className='capture-desc'>拍摄或上传图片，AI 自动分析美学构成</Text>
          </View>

          <View className='capture-options'>
            <View className='capture-option' onClick={this.chooseImage.bind(this, ['camera'])}>
              <Text>📷 拍照</Text>
            </View>
            <View className='capture-option' onClick={this.chooseImage.bind(this, ['album'])}>
              <Text>🖼️ 相册</Text>
            </View>
          </View>
        </View>

        {/* 最近分析 */}
        <View className='section'>
          <View className='section-title'>
            <Text>最近分析</Text>
            <Text className='more' onClick={this.loadHistory.bind(this)}>刷新</Text>
          </View>

          {history.length > 0 ? (
            <ScrollView className='history-list' scrollX>
              {history.slice(0, 6).map((item, index) => (
                <View key={index} className='history-item' onClick={this.viewHistory.bind(this, item)}>
                  <Image className='history-image' src={item.image_url} mode='aspectFill' />
                  <Text className='history-paradigm'>{item.paradigm || '未知'}</Text>
                  <Text className='history-score'>{item.total_score || 0}分 · W(T)={(item.wt || 0).toFixed(2)}</Text>
                </View>
              ))}
            </ScrollView>
          ) : (
            <View className='empty-state'>
              <Text className='empty-icon'>📊</Text>
              <Text className='empty-text'>还没有分析记录，拍一张试试吧</Text>
            </View>
          )}
        </View>

        {/* 精选案例 */}
        <View className='section'>
          <View className='section-title'>
            <Text>精选案例</Text>
          </View>
          <View className='case-grid'>
            {FEATURED_CASES.map((item, index) => (
              <View key={index} className='case-card'>
                <Image className='case-image' src={item.image} mode='aspectFill' />
                <View className='case-info'>
                  <Text className='case-name'>{item.name}</Text>
                  <Text className='case-meta'>{item.paradigm} · {item.score}分</Text>
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* 底部说明 */}
        <View className='footer safe-bottom'>
          <Text className='footer-text'>BEA 双极情绪美学 · 让美可量化、可分析、可设计</Text>
          <Text className='footer-text'>美感 = 可控张力下的情绪奖赏</Text>
        </View>
      </View>
    )
  }
}
