# BEA 跨端小程序

双极情绪美学（Bipolar Emotion Aesthetics）跨端小程序 - 基于 Taro 框架，一次开发，支持微信小程序、抖音小程序、H5 三端运行。

## 功能特性

- 📸 **拍照分析**：拍摄或上传图片，AI 自动分析美学构成
- 🧠 **智能识别**：多模态大模型自动识别 6 维度视觉元素极性
- 📊 **完整报告**：W(T)、范式定位、四象限、四维评分、病症诊断、优化处方
- 💾 **历史记录**：本地保存分析历史，随时回看
- 🔗 **原生分享**：微信/抖音原生分享能力
- 📱 **三端运行**：微信小程序 + 抖音小程序 + H5

## 技术栈

- **框架**：Taro 3.6 + React 18
- **样式**：Sass
- **图表**：ECharts（H5）/ ec-canvas（小程序）
- **后端**：复用 mobile/backend Flask API
- **AI**：豆包视觉（Doubao Vision）

## 快速开始

### 1. 安装依赖

```bash
cd bea-miniapp
npm install
```

### 2. 配置 API 地址

编辑 `config/index.js`，修改 `API_BASE_URL` 为你的后端地址：

```js
defineConstants: {
  API_BASE_URL: JSON.stringify('https://your-api-domain.com')
}
```

### 3. 开发调试

```bash
# 微信小程序
npm run dev:weapp

# 抖音小程序
npm run dev:tt

# H5
npm run dev:h5
```

### 4. 构建生产版本

```bash
# 微信小程序
npm run build:weapp

# 抖音小程序
npm run build:tt

# H5
npm run build:h5
```

## 平台配置

### 微信小程序

1. 注册微信小程序账号：https://mp.weixin.qq.com/
2. 获取 AppID，填入 `project.config.json`
3. 在小程序后台配置合法域名（request、uploadFile）
4. 使用微信开发者工具导入 `dist/` 目录
5. 提交审核并发布

### 抖音小程序

1. 注册抖音小程序账号：https://developer.open-douyin.com/
2. 获取 AppID，填入 `project.tt.json`
3. 在小程序后台配置合法域名
4. 使用抖音开发者工具导入 `dist/` 目录
5. 提交审核并发布

### H5

1. 构建后将 `dist/` 目录部署到静态服务器
2. 配置反向代理到后端 API
3. 绑定域名并配置 HTTPS

## 项目结构

```
bea-miniapp/
├── src/
│   ├── pages/
│   │   ├── index/           # 首页（拍照/上传、历史、精选案例）
│   │   ├── analyze/         # 分析中页面（步骤动画）
│   │   └── report/          # 报告页（6卡片+图表）
│   ├── components/          # 公共组件
│   ├── utils/
│   │   ├── api.js           # API 封装
│   │   └── storage.js       # 存储封装
│   ├── images/              # 图片资源
│   ├── app.js               # 入口文件
│   ├── app.config.js        # 应用配置
│   └── app.scss             # 全局样式
├── config/
│   ├── index.js             # Taro 主配置
│   ├── dev.js               # 开发配置
│   └── prod.js              # 生产配置
├── project.config.json      # 微信小程序配置
├── project.tt.json          # 抖音小程序配置
├── package.json
└── README.md
```

## 后端 API

复用 `mobile/backend/` 的 Flask API，主要接口：

| 接口 | 方法 | 说明 |
|---|---|---|
| `/api/analyze` | POST | 图片分析（multipart/form-data） |
| `/api/health` | GET | 健康检查 |
| `/api/history` | GET | 历史记录列表 |
| `/api/history/:id` | GET | 历史详情 |

## BEA 理论核心

- **美感 = 可控张力下的情绪奖赏**
- **亲极 P+**：圆润、柔色、光滑、舒缓、对称、留白、稳定
- **危极 T−**：尖锐、强对比、坚硬、突变、失衡、拥挤、冷峻
- **W(T) 危极权重**：0-1，衡量整体危极占比
- **8 大范式**：治愈松弛、亲和精致、诗意朦胧、均衡典雅、崇高震撼、冷峻克制、神秘魅惑、先锋反叛

## 部署注意事项

1. **域名备案**：小程序要求 API 域名必须已备案且支持 HTTPS
2. **合法域名配置**：在各平台小程序后台配置 request 和 uploadFile 合法域名
3. **图片大小限制**：小程序上传图片建议压缩到 2MB 以内
4. **审核规范**：确保内容符合各平台小程序审核规范
5. **用户隐私**：图片分析后建议自动删除，不长期存储用户图片

## 许可证

CC BY 4.0 - 双极情绪美学理论由星空本空创立

## 联系方式

- 理论官网：https://maxing0000.github.io/bipolar-emotion-aesthetics/
- GitHub：https://github.com/Maxing0000/bipolar-emotion-aesthetics
