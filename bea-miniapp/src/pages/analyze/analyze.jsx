import { Component } from 'react'
import { View, Text, Image } from '@tarojs/components'
import Taro, { useRouter } from '@tarojs/taro'
import { analyzeImage } from '../../utils/api'
import { saveToHistory, saveCurrentResult } from '../../utils/storage'
import './analyze.scss'

const STEPS = [
  { id: 1, text: '图片预处理' },
  { id: 2, text: 'AI 识别视觉元素' },
  { id: 3, text: '计算 W(T) 危极权重' },
  { id: 4, text: '范式定位与评分' },
  { id: 5, text: '病症诊断与处方' },
]

export default class Analyze extends Component {
  config = {
    navigationBarTitleText: '分析中...'
  }

  constructor(props) {
    super(props)
    this.state = {
      filePath: '',
      currentStep: 1,
      error: ''
    }
  }

  componentDidMount() {
    // 获取路由参数
    const router = this.$router || this.props.router
    const filePath = router?.params?.filePath || ''

    if (filePath) {
      this.setState({ filePath: decodeURIComponent(filePath) })
      this.startAnalysis(decodeURIComponent(filePath))
    } else {
      Taro.showToast({ title: '未获取到图片', icon: 'none' })
      setTimeout(() => Taro.navigateBack(), 1500)
    }
  }

  // 开始分析
  async startAnalysis(filePath) {
    try {
      // 步骤动画
      this.stepAnimation()

      // 调用 API
      const result = await analyzeImage(filePath)

      // 保存结果
      saveCurrentResult(result)
      saveToHistory(result)

      // 跳转到报告页
      setTimeout(() => {
        Taro.redirectTo({ url: '/pages/report/report' })
      }, 500)

    } catch (error) {
      console.error('分析失败:', error)
      this.setState({ error: error.message || '分析失败' })
      Taro.showModal({
        title: '分析失败',
        content: error.message || '请检查网络连接后重试',
        showCancel: true,
        cancelText: '返回',
        confirmText: '重试',
        success: (res) => {
          if (res.confirm) {
            this.startAnalysis(filePath)
          } else {
            Taro.navigateBack()
          }
        }
      })
    }
  }

  // 步骤动画
  stepAnimation() {
    let step = 1
    const interval = setInterval(() => {
      if (step < STEPS.length) {
        step++
        this.setState({ currentStep: step })
      } else {
        clearInterval(interval)
      }
    }, 800)
  }

  render() {
    const { filePath, currentStep } = this.state

    return (
      <View className='analyze-page'>
        <Image className='analyze-image' src={filePath} mode='aspectFill' />

        <View className='loader'>
          <View className='loader-ring loader-ring-1'></View>
          <View className='loader-ring loader-ring-2'></View>
        </View>

        <Text className='analyze-title'>AI 正在分析中...</Text>
        <Text className='analyze-desc'>识别视觉元素，计算双极构成</Text>

        <View className='analyze-steps'>
          {STEPS.map((step) => (
            <View
              key={step.id}
              className={`analyze-step ${currentStep >= step.id ? 'done' : ''} ${currentStep === step.id ? 'active' : ''}`}
            >
              <View className='step-dot'>
                {currentStep > step.id ? '✓' : step.id}
              </View>
              <Text className='step-text'>{step.text}</Text>
            </View>
          ))}
        </View>

        <Text className='analyze-tip'>首次分析约需 3-5 秒，请稍候...</Text>
      </View>
    )
  }
}
