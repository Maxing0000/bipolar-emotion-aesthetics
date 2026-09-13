import { Component } from 'react'
import { View, Text, Image, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { getCurrentResult } from '../../utils/storage'
import './report.scss'

export default class Report extends Component {
  config = {
    navigationBarTitleText: 'BEA 分析报告'
  }

  constructor(props) {
    super(props)
    this.state = {
      result: null,
      showShare: false
    }
  }

  componentDidMount() {
    const result = getCurrentResult()
    if (result) {
      this.setState({ result })
    } else {
      Taro.showToast({ title: '未找到分析结果', icon: 'none' })
      setTimeout(() => Taro.redirectTo({ url: '/pages/index/index' }), 1500)
    }
  }

  // 返回首页
  goHome() {
    Taro.redirectTo({ url: '/pages/index/index' })
  }

  // 分享
  onShareAppMessage() {
    const { result } = this.state
    return {
      title: `BEA美学分析：${result?.paradigm?.name || '未知'}，评分${result?.total_score || 0}分`,
      path: '/pages/index/index'
    }
  }

  // 显示分享弹窗
  showShareModal() {
    this.setState({ showShare: true })
  }

  // 隐藏分享弹窗
  hideShareModal() {
    this.setState({ showShare: false })
  }

  render() {
    const { result, showShare } = this.state
    if (!result) return null

    const { paradigm, wt, total_score, scores, quadrant, diagnoses, prescriptions, elements, mood, image_url } = result

    return (
      <View className='report-page'>
        <ScrollView scrollY className='report-scroll'>
          {/* 报告头部 */}
          <View className='report-header'>
            <Image className='report-image' src={image_url} mode='aspectFill' />
            <View className='report-overlay'>
              <View className='paradigm-badge'>{paradigm?.name || '未知'}</View>
              <Text className='report-title'>美学分析报告</Text>
              <Text className='report-wt'>W(T) 危极权重：{wt?.toFixed(2)} · 总分 {total_score}/100</Text>
            </View>
          </View>

          {/* 报告内容 */}
          <View className='report-content'>
            {/* 卡片1：情绪基调 */}
            <View className='report-card'>
              <View className='card-title'>
                <Text className='card-icon'>💭</Text>
                <Text>情绪基调</Text>
              </View>
              <Text className='mood-text'>{mood || ''}</Text>
            </View>

            {/* 卡片2：双极构成 */}
            <View className='report-card'>
              <View className='card-title'>
                <Text className='card-icon'>⚖️</Text>
                <Text>双极构成</Text>
              </View>
              <View className='bipolar-grid'>
                <View className='bipolar-col positive'>
                  <Text className='col-title'>亲极 P+（安抚）</Text>
                  <View className='element-list'>
                    {(elements?.positive || []).map((item, i) => (
                      <Text key={i} className='element-item'>{item}</Text>
                    ))}
                    {(elements?.positive || []).length === 0 && (
                      <Text className='element-item empty'>暂无明显亲极元素</Text>
                    )}
                  </View>
                </View>
                <View className='bipolar-col negative'>
                  <Text className='col-title'>危极 T−（唤醒）</Text>
                  <View className='element-list'>
                    {(elements?.negative || []).map((item, i) => (
                      <Text key={i} className='element-item'>{item}</Text>
                    ))}
                    {(elements?.negative || []).length === 0 && (
                      <Text className='element-item empty'>暂无明显危极元素</Text>
                    )}
                  </View>
                </View>
              </View>
            </View>

            {/* 卡片3：四象限定位 */}
            <View className='report-card'>
              <View className='card-title'>
                <Text className='card-icon'>🎯</Text>
                <Text>四象限定位</Text>
              </View>
              <View className='quadrant-box'>
                <View className='quadrant-grid'>
                  <View className='quadrant-cell q1'>平庸区</View>
                  <View className='quadrant-cell q2'>黄金区</View>
                  <View className='quadrant-cell q3'>混沌区</View>
                  <View className='quadrant-cell q4'>焦虑区</View>
                </View>
                <View
                  className='quadrant-dot'
                  style={{
                    left: `${(quadrant?.order || 0.5) * 100}%`,
                    bottom: `${(quadrant?.tension || 0.5) * 100}%`
                  }}
                ></View>
              </View>
              <Text className='quadrant-advice'>{quadrant?.advice || ''}</Text>
            </View>

            {/* 卡片4：四维评分 */}
            <View className='report-card'>
              <View className='card-title'>
                <Text className='card-icon'>📊</Text>
                <Text>四维评分</Text>
              </View>
              <View className='score-overview'>
                <View className='score-item'>
                  <Text className='score-value'>{scores?.tension || 0}</Text>
                  <Text className='score-label'>双极张力</Text>
                </View>
                <View className='score-item'>
                  <Text className='score-value'>{scores?.order || 0}</Text>
                  <Text className='score-label'>结构秩序</Text>
                </View>
                <View className='score-item'>
                  <Text className='score-value'>{scores?.threshold || 0}</Text>
                  <Text className='score-label'>阈值安全</Text>
                </View>
                <View className='score-item'>
                  <Text className='score-value'>{scores?.context || 0}</Text>
                  <Text className='score-label'>语境适配</Text>
                </View>
              </View>
              {/* 评分条 */}
              <View className='score-bars'>
                {Object.entries(scores || {}).map(([key, value]) => (
                  <View key={key} className='score-bar-row'>
                    <Text className='score-bar-label'>{
                      {tension: '张力', order: '秩序', threshold: '阈值', context: '语境'}[key] || key
                    }</Text>
                    <View className='score-bar-track'>
                      <View className='score-bar-fill' style={{ width: `${(value / 25) * 100}%` }}></View>
                    </View>
                    <Text className='score-bar-value'>{value}/25</Text>
                  </View>
                ))}
              </View>
            </View>

            {/* 卡片5：病症诊断 */}
            <View className='report-card'>
              <View className='card-title'>
                <Text className='card-icon'>🔍</Text>
                <Text>病症诊断</Text>
              </View>
              {diagnoses && diagnoses.length > 0 ? (
                diagnoses.map((d, i) => (
                  <View key={i} className='diagnosis-item'>
                    <Text className='diagnosis-name'>{d.name}</Text>
                    <Text className='diagnosis-desc'>{d.desc}</Text>
                  </View>
                ))
              ) : (
                <View className='no-diagnosis'>
                  <Text className='no-diagnosis-icon'>✅</Text>
                  <Text className='no-diagnosis-text'>未发现明显审美病症，整体构成健康</Text>
                </View>
              )}
            </View>

            {/* 卡片6：优化处方 */}
            <View className='report-card'>
              <View className='card-title'>
                <Text className='card-icon'>💊</Text>
                <Text>优化处方</Text>
              </View>
              {prescriptions && prescriptions.length > 0 ? (
                prescriptions.map((p, i) => (
                  <View key={i} className='prescription-item'>
                    <View className='prescription-num'>{i + 1}</View>
                    <Text className='prescription-text'>{p}</Text>
                  </View>
                ))
              ) : (
                <Text className='no-prescription'>当前构成已较优，保持现有设计即可</Text>
              )}
            </View>
          </View>

          {/* 底部占位 */}
          <View style={{ height: '120px' }}></View>
        </ScrollView>

        {/* 底部操作栏 */}
        <View className='report-actions safe-bottom'>
          <View className='action-btn secondary' onClick={this.goHome.bind(this)}>
            <Text>再拍一张</Text>
          </View>
          <Button className='action-btn primary' openType='share'>
            <Text>分享报告</Text>
          </Button>
        </View>
      </View>
    )
  }
}
