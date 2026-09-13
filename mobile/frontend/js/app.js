/**
 * BEA 移动端 MVP - 主逻辑
 * 负责：文件上传、API调用、分析动画、报告渲染、图表、历史记录、分享
 */

// ============ 全局变量 ============
let currentResult = null;
let quadrantChartInstance = null;
let radarChartInstance = null;

// 精选案例数据
const FEATURED_CASES = [
  { name: "iPhone 17 Pro", paradigm: "崇高震撼", score: 86, image: "https://maxing0000.github.io/bipolar-emotion-aesthetics/cases/images/01-iphone17-pro.jpg" },
  { name: "尊界 S800", paradigm: "崇高震撼", score: 94, image: "https://maxing0000.github.io/bipolar-emotion-aesthetics/cases/images/02-zunjie-s800.jpg" },
  { name: "小米 SU7", paradigm: "冷峻克制", score: 84, image: "https://maxing0000.github.io/bipolar-emotion-aesthetics/cases/images/03-xiaomi-su7.jpg" },
  { name: "奔驰 S 级", paradigm: "均衡典雅", score: 89, image: "https://maxing0000.github.io/bipolar-emotion-aesthetics/cases/images/07-mercedes-s-class.jpg" },
];

// ============ 文件上传 ============
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件');
    return;
  }

  // 验证文件大小
  if (file.size > 10 * 1024 * 1024) {
    alert('图片大小不能超过 10MB');
    return;
  }

  // 显示分析中页面
  showAnalyzePage(file);

  // 开始分析
  analyzeImage(file);
}

function showAnalyzePage(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    document.getElementById('analyzeImage').src = e.target.result;
  };
  reader.readAsDataURL(file);

  document.getElementById('analyzePage').classList.remove('hidden');
  document.body.style.overflow = 'hidden';

  // 重置步骤
  document.querySelectorAll('.analyze-step').forEach((step, index) => {
    step.classList.remove('active', 'done');
    if (index === 0) step.classList.add('active');
  });

  // 步骤动画
  animateSteps();
}

function animateSteps() {
  const steps = document.querySelectorAll('.analyze-step');
  let currentStep = 0;

  const interval = setInterval(() => {
    if (currentStep < steps.length) {
      steps[currentStep].classList.remove('active');
      steps[currentStep].classList.add('done');
      currentStep++;
      if (currentStep < steps.length) {
        steps[currentStep].classList.add('active');
      }
    } else {
      clearInterval(interval);
    }
  }, 800);
}

function hideAnalyzePage() {
  document.getElementById('analyzePage').classList.add('hidden');
  document.body.style.overflow = '';
}

// ============ API 调用 ============
async function analyzeImage(file) {
  try {
    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || '分析失败');
    }

    const result = await response.json();
    currentResult = result;

    // 保存到 sessionStorage
    sessionStorage.setItem('beaResult', JSON.stringify(result));

    // 保存到 localStorage（历史记录）
    saveToLocalHistory(result);

    // 跳转到报告页
    setTimeout(() => {
      hideAnalyzePage();
      window.location.href = 'report.html';
    }, 1000);

  } catch (error) {
    console.error('分析失败:', error);
    hideAnalyzePage();
    alert('分析失败: ' + error.message + '\n请检查网络连接后重试');
  }
}

// ============ 报告渲染 ============
function renderReport(result) {
  currentResult = result;

  // 头部信息
  document.getElementById('reportImage').src = result.image_url || '';
  document.getElementById('reportParadigm').textContent = result.paradigm?.name || '未知';
  document.getElementById('reportWt').textContent = result.wt?.toFixed(2) || '0.00';
  document.getElementById('reportScore').textContent = result.total_score || 0;

  // 情绪基调
  document.getElementById('reportMood').innerHTML = result.mood || '';

  // 双极构成
  renderElements(result.elements);

  // 四象限
  renderQuadrantChart(result.quadrant);

  // 四维评分
  renderScores(result.scores);
  renderRadarChart(result.scores);

  // 病症诊断
  renderDiagnoses(result.diagnoses);

  // 优化处方
  renderPrescriptions(result.prescriptions);
}

function renderElements(elements) {
  const positiveList = document.getElementById('positiveElements');
  const negativeList = document.getElementById('negativeElements');

  positiveList.innerHTML = '';
  negativeList.innerHTML = '';

  (elements?.positive || []).forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    positiveList.appendChild(li);
  });

  (elements?.negative || []).forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    negativeList.appendChild(li);
  });

  if ((elements?.positive || []).length === 0) {
    positiveList.innerHTML = '<li>暂无明显亲极元素</li>';
  }
  if ((elements?.negative || []).length === 0) {
    negativeList.innerHTML = '<li>暂无明显危极元素</li>';
  }
}

function renderQuadrantChart(quadrant) {
  const chartDom = document.getElementById('quadrantChart');
  if (!chartDom) return;

  if (quadrantChartInstance) {
    quadrantChartInstance.dispose();
  }

  quadrantChartInstance = echarts.init(chartDom);

  const option = {
    grid: { left: 50, right: 20, top: 30, bottom: 40 },
    xAxis: {
      name: '秩序 →',
      nameLocation: 'middle',
      nameGap: 25,
      min: 0, max: 1,
      splitLine: { show: true, lineStyle: { type: 'dashed' } },
      axisLabel: { show: false },
    },
    yAxis: {
      name: '张力 →',
      nameLocation: 'middle',
      nameGap: 35,
      min: 0, max: 1,
      splitLine: { show: true, lineStyle: { type: 'dashed' } },
      axisLabel: { show: false },
    },
    series: [{
      type: 'scatter',
      symbolSize: 20,
      data: [[quadrant?.order || 0.5, quadrant?.tension || 0.5]],
      itemStyle: {
        color: new echarts.graphic.RadialGradient(0.5, 0.5, 0.5, [
          { offset: 0, color: '#FF6B35' },
          { offset: 1, color: '#2EC4B6' },
        ]),
        shadowBlur: 10,
        shadowColor: 'rgba(255,107,53,0.5)',
      },
      label: {
        show: true,
        formatter: quadrant?.name?.split('（')[0] || '',
        position: 'top',
        fontSize: 12,
        fontWeight: 'bold',
        color: '#1A1A2E',
      },
    }],
    graphic: [
      { type: 'text', left: '25%', top: '20%', style: { text: '平庸区', fill: '#9CA3AF', fontSize: 12 } },
      { type: 'text', left: '70%', top: '20%', style: { text: '黄金区', fill: '#2EC4B6', fontSize: 12, fontWeight: 'bold' } },
      { type: 'text', left: '25%', top: '75%', style: { text: '混沌区', fill: '#9CA3AF', fontSize: 12 } },
      { type: 'text', left: '70%', top: '75%', style: { text: '焦虑区', fill: '#EF4444', fontSize: 12 } },
    ],
  };

  quadrantChartInstance.setOption(option);

  document.getElementById('quadrantAdvice').textContent = quadrant?.advice || '';
}

function renderScores(scores) {
  document.getElementById('scoreTension').textContent = scores?.tension || 0;
  document.getElementById('scoreOrder').textContent = scores?.order || 0;
  document.getElementById('scoreThreshold').textContent = scores?.threshold || 0;
  document.getElementById('scoreContext').textContent = scores?.context || 0;
}

function renderRadarChart(scores) {
  const chartDom = document.getElementById('radarChart');
  if (!chartDom) return;

  if (radarChartInstance) {
    radarChartInstance.dispose();
  }

  radarChartInstance = echarts.init(chartDom);

  const option = {
    radar: {
      indicator: [
        { name: '双极张力', max: 25 },
        { name: '结构秩序', max: 25 },
        { name: '阈值安全', max: 25 },
        { name: '语境适配', max: 25 },
      ],
      radius: '65%',
      axisName: { color: '#6B7280', fontSize: 12 },
      splitArea: {
        areaStyle: {
          color: ['rgba(255,107,53,0.05)', 'rgba(46,196,182,0.05)'],
        },
      },
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          scores?.tension || 0,
          scores?.order || 0,
          scores?.threshold || 0,
          scores?.context || 0,
        ],
        name: 'BEA 评分',
        areaStyle: {
          color: new echarts.graphic.RadialGradient(0.5, 0.5, 0.5, [
            { offset: 0, color: 'rgba(255,107,53,0.4)' },
            { offset: 1, color: 'rgba(46,196,182,0.4)' },
          ]),
        },
        lineStyle: { color: '#FF6B35', width: 2 },
        itemStyle: { color: '#FF6B35' },
      }],
    }],
  };

  radarChartInstance.setOption(option);
}

function renderDiagnoses(diagnoses) {
  const list = document.getElementById('diagnosisList');

  if (!diagnoses || diagnoses.length === 0) {
    list.innerHTML = `
      <div class="no-diagnosis">
        <div class="icon">✅</div>
        <div>未发现明显审美病症，整体构成健康</div>
      </div>
    `;
    return;
  }

  list.innerHTML = '';
  diagnoses.forEach(d => {
    const item = document.createElement('div');
    item.className = 'diagnosis-item';
    item.innerHTML = `
      <div class="name">${d.name}</div>
      <div class="desc">${d.desc}</div>
    `;
    list.appendChild(item);
  });
}

function renderPrescriptions(prescriptions) {
  const list = document.getElementById('prescriptionList');

  if (!prescriptions || prescriptions.length === 0) {
    list.innerHTML = '<div style="text-align:center;color:var(--bea-gray);padding:20px">当前构成已较优，保持现有设计即可</div>';
    return;
  }

  list.innerHTML = '';
  prescriptions.forEach((p, index) => {
    const item = document.createElement('div');
    item.className = 'prescription-item';
    item.innerHTML = `
      <div class="num">${index + 1}</div>
      <div class="text">${p}</div>
    `;
    list.appendChild(item);
  });
}

// ============ 历史记录 ============
function saveToLocalHistory(result) {
  try {
    let history = JSON.parse(localStorage.getItem('beaHistory') || '[]');
    history.unshift({
      id: result.history_id || Date.now(),
      timestamp: new Date().toISOString(),
      image_url: result.image_url,
      paradigm: result.paradigm?.name,
      wt: result.wt,
      total_score: result.total_score,
      result: result,
    });
    // 只保留最近20条
    history = history.slice(0, 20);
    localStorage.setItem('beaHistory', JSON.stringify(history));
  } catch (e) {
    console.error('保存历史失败:', e);
  }
}

function loadHistory() {
  try {
    const history = JSON.parse(localStorage.getItem('beaHistory') || '[]');
    const list = document.getElementById('historyList');

    if (history.length === 0) {
      list.innerHTML = `
        <div class="empty-state" style="width:100%">
          <div class="icon">📊</div>
          <div class="text">还没有分析记录，拍一张试试吧</div>
        </div>
      `;
      return;
    }

    list.innerHTML = '';
    history.slice(0, 6).forEach(item => {
      const div = document.createElement('div');
      div.className = 'history-item';
      div.onclick = () => {
        sessionStorage.setItem('beaResult', JSON.stringify(item.result));
        window.location.href = 'report.html';
      };
      div.innerHTML = `
        <img src="${item.image_url || ''}" alt="">
        <div class="paradigm">${item.paradigm || ''}</div>
        <div class="score">${item.total_score || 0}分 · W(T)=${item.wt?.toFixed(2) || '0'}</div>
      `;
      list.appendChild(div);
    });
  } catch (e) {
    console.error('加载历史失败:', e);
  }
}

// ============ 精选案例 ============
function loadFeaturedCases() {
  const grid = document.getElementById('caseGrid');
  if (!grid) return;

  grid.innerHTML = '';
  FEATURED_CASES.forEach(c => {
    const card = document.createElement('div');
    card.className = 'case-card';
    card.innerHTML = `
      <img src="${c.image}" alt="${c.name}" loading="lazy">
      <div class="info">
        <div class="name">${c.name}</div>
        <div class="meta">${c.paradigm} · ${c.score}分</div>
      </div>
    `;
    grid.appendChild(card);
  });
}

// ============ 分享功能 ============
function showShare() {
  if (!currentResult) return;

  document.getElementById('shareImage').src = currentResult.image_url || '';
  document.getElementById('shareParadigm').textContent = currentResult.paradigm?.name || '';
  document.getElementById('shareScore').textContent = currentResult.total_score || 0;
  document.getElementById('shareWt').textContent = currentResult.wt?.toFixed(2) || '0';

  document.getElementById('shareModal').classList.remove('hidden');
}

function hideShare(event) {
  if (event && event.target !== event.currentTarget) return;
  document.getElementById('shareModal').classList.add('hidden');
}

// ============ 导航 ============
function goBack() {
  window.location.href = 'index.html';
}

// ============ 页面初始化 ============
document.addEventListener('DOMContentLoaded', function() {
  // 如果是首页，加载历史和案例
  if (document.getElementById('historyList')) {
    loadHistory();
    loadFeaturedCases();
  }

  // 窗口大小变化时重绘图表
  window.addEventListener('resize', function() {
    if (quadrantChartInstance) quadrantChartInstance.resize();
    if (radarChartInstance) radarChartInstance.resize();
  });
});
