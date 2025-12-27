# Railway 部署指南 - 5分钟完成

## 为什么选择 Railway？
- ✅ 比 Zeabur 更稳定（很多开发者使用）
- ✅ 更好的日志和监控
- ✅ 自动 HTTPS 和域名
- ✅ 每月 $5 免费额度（足够个人项目）
- ✅ 支持自动部署（git push 就部署）

---

## 🚀 快速部署步骤（5分钟）

### 步骤 1：注册 Railway（1分钟）
1. 访问 https://railway.app
2. 点击 "Start a New Project"
3. 使用 GitHub 登录
4. 绑定信用卡验证（不会扣费，只是验证）

### 步骤 2：部署项目（2分钟）
1. 点击 "Deploy from GitHub repo"
2. 选择 `kkong0010/my-meshy-backend` 仓库
3. Railway 自动检测到 Python 项目
4. 点击 "Deploy Now"

**Railway 会自动**：
- 读取 requirements.txt
- 读取 Procfile（我们已经配置好了：`web: python api.py`）
- 分配域名
- 启动服务

### 步骤 3：配置环境变量（2分钟）
1. 进入项目 → Variables 标签
2. 添加环境变量：
   ```
   REPLICATE_API_TOKEN=your_replicate_token_here
   MESHY_API_KEY=your_meshy_key_here
   ```
3. 点击 "Add" 保存
4. Railway 自动重新部署

### 步骤 4：获取域名
1. 进入 Settings 标签
2. 点击 "Generate Domain"
3. 复制域名（类似：`your-project.up.railway.app`）

---

## ✅ 完成！

现在你的 API 应该运行在：
- `https://your-project.up.railway.app/` - 主页
- `https://your-project.up.railway.app/api/health` - 健康检查
- `https://your-project.up.railway.app/api/generate` - 生成接口

---

## 🔧 Railway vs Zeabur 对比

| 特性 | Railway | Zeabur |
|------|---------|---------|
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 日志 | 清晰详细 | 有时混乱 |
| PORT 配置 | 自动正确 | 经常有问题 |
| 社区支持 | 大量教程 | 较少 |
| 免费额度 | $5/月 | 免费但不稳定 |
| 部署速度 | 快 | 快 |

---

## 💡 如果 Railway 也不行（极少情况）

还有备选方案：

### Plan D: Render.com（完全免费）
- 访问 https://render.com
- 类似 Railway 的操作
- 完全免费（但服务器会休眠，首次访问慢）

### Plan E: 本地运行 + ngrok（临时方案）
```bash
# 本地运行
python api.py

# 另一个终端
ngrok http 8080
# 获得临时公网 URL
```

---

## 🎯 推荐行动

1. **现在**：等待当前 Zeabur 部署（已删除 gunicorn）
2. **如果 502**：立即切换到 Railway（5分钟）
3. **Railway 优势**：PORT 配置从未出过问题！

---

## 📞 需要帮助？

告诉我部署进度，我随时帮你：
1. Railway 注册问题
2. 环境变量配置
3. 域名设置
4. 任何错误排查

Railway 是更成熟的平台，99% 能一次成功！
