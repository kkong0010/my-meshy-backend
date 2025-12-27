# 🎨 Tripo 3D 魔法工坊

一个基于 Tripo API 的高颜值 3D 模型生成应用，使用 React + Tailwind CSS 打造治愈系界面。

## ✨ 功能特性

- 📸 **图片上传**：支持拖拽上传和点击上传
- 🎯 **智能生成**：基于 Tripo AI 将 2D 图片转换为 3D 模型
- 🎨 **高颜值 UI**：渐变背景、毛玻璃效果、流畅动画
- ⚙️ **参数配置**：支持模型版本、纹理质量、PBR 材质选择
- 👁️ **实时预览**：使用 Google Model Viewer 实时查看 3D 模型
- ⬇️ **一键下载**：生成后可直接下载 GLB 格式模型

## 📦 技术栈

### 前端
- React 18
- Vite
- Tailwind CSS
- Axios
- Lucide React (图标)
- Google Model Viewer

### 后端
- Flask
- Flask-CORS
- Requests
- Tripo 3D API

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装前端依赖
npm install

# 安装后端依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `api_key.txt` 文件，写入你的 Tripo API Key：

```
tsk_your_api_key_here
```

### 3. 启动应用

**方式一：分别启动（推荐调试）**

```bash
# 终端 1 - 启动后端 API
python api.py

# 终端 2 - 启动前端开发服务器
npm run dev
```

**方式二：使用 npm scripts**

```bash
# 启动后端
npm run api

# 启动前端（另开终端）
npm run dev
```

### 4. 访问应用

打开浏览器访问：`http://localhost:3000`

## 📁 项目结构

```
hackathon-3d/
├── src/
│   ├── pages/
│   │   └── Tripo3D.jsx          # 主页面组件
│   ├── App.jsx                  # 应用根组件
│   ├── main.jsx                 # 入口文件
│   └── index.css                # 全局样式
├── static/
│   ├── uploads/                 # 上传的图片
│   └── models/                  # 生成的模型
├── api.py                       # Flask 后端 API
├── api_key.txt                  # Tripo API Key（需自行创建）
├── package.json                 # 前端依赖配置
├── requirements.txt             # Python 依赖配置
├── vite.config.js               # Vite 配置
├── tailwind.config.js           # Tailwind CSS 配置
└── index.html                   # HTML 模板

```

## 🎯 API 端点

### `POST /api/generate`

生成 3D 模型

**请求参数：**
- `file`: 图片文件（multipart/form-data）
- `model_version`: 模型版本（可选，默认 v2.5-20250123）
- `pbr`: 是否启用 PBR（可选，默认 true）
- `texture_quality`: 纹理质量（可选，standard/detailed）

**响应：**
```json
{
  "success": true,
  "model_url": "/static/models/model_xxx.glb",
  "task_id": "task_id_here"
}
```

### `GET /api/health`

健康检查

**响应：**
```json
{
  "status": "ok",
  "api_key_loaded": true
}
```

## ⚙️ 配置选项

### 模型版本

- **v2.5-20250123**（推荐）：平衡质量和速度
- **v3.0-20250812**：最新版本，质量更高
- **Turbo-v1.0-20250506**：快速生成

### 纹理质量

- **standard**：标准质量，速度快
- **detailed**：精细质量，细节更丰富

### PBR 材质

- 启用后生成物理真实渲染材质
- 提供更真实的光照和反射效果

## 🎨 设计特色

1. **治愈系配色**：柔和的紫粉蓝渐变背景
2. **毛玻璃效果**：backdrop-blur 实现卡片半透明
3. **流畅动画**：浮动、脉冲、渐入等自定义动画
4. **响应式布局**：适配桌面和移动设备
5. **友好交互**：拖拽上传、实时反馈、错误提示

## 🔧 常见问题

### Q: 生成时间较长怎么办？
A: Tripo API 生成通常需要 1-3 分钟，请耐心等待。后端设置了 10 分钟超时。

### Q: 支持哪些图片格式？
A: 支持 JPG、PNG、WEBP 格式，分辨率建议 256×256 至 6000×6000 像素。

### Q: 如何获取 Tripo API Key？
A: 访问 [Tripo 官网](https://tripo3d.ai) 注册账号并获取 API Key。

### Q: 生成失败怎么办？
A: 检查：
1. API Key 是否正确
2. 图片格式和尺寸是否符合要求
3. 网络连接是否正常
4. 后端日志中的详细错误信息

## 📝 待优化

- [ ] 添加实时进度更新（WebSocket）
- [ ] 支持批量生成
- [ ] 历史记录管理
- [ ] 模型编辑和优化功能
- [ ] 更多导出格式（OBJ、FBX 等）

## 📄 许可证

MIT License

## 🙏 致谢

- [Tripo 3D](https://tripo3d.ai) - AI 3D 生成 API
- [Tailwind CSS](https://tailwindcss.com) - CSS 框架
- [Google Model Viewer](https://modelviewer.dev) - 3D 模型查看器
- [Lucide](https://lucide.dev) - 图标库

---

Made with ❤️ by Your Team
