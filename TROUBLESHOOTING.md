# Zeabur 部署故障排查指南

## 🔍 步骤 1：查看 Zeabur 日志

1. 进入 Zeabur 控制台
2. 点击你的服务 → "日志" 标签
3. 查找以下关键信息：

### ✅ 成功的标志：
```
[STARTING] Tripo 3D API Server v2.0-no-startup-tests
[PORT] 8080 (或其他端口)
[HOST] 0.0.0.0
[IMPORTANT] NO STARTUP TESTS
Booting worker with pid: xxx
```

### ❌ 失败的标志：
```
test_input.png
You don't have enough credit
ModuleNotFoundError
Port already in use
```

---

## 🛠️ 步骤 2：检查清单

### A. 环境变量检查（在 Zeabur 控制台设置）
- [ ] `REPLICATE_API_TOKEN` - 已设置？
- [ ] `MESHY_API_KEY` - 已设置？
- [ ] `PORT` - Zeabur 会自动设置，不需要手动添加

### B. 文件检查（本地）
- [ ] `main.py` 已删除或重命名为 `.backup`？
- [ ] `api.py` 存在？
- [ ] `Zbfile` 内容：`default: gunicorn --bind 0.0.0.0:$PORT --timeout 600 --workers 1 api:app`
- [ ] `requirements.txt` 包含 `gunicorn==21.2.0`？

### C. Git 检查
```bash
git log -1 --oneline
# 应该显示: CRITICAL FIX: Remove main.py...
```

---

## 🚨 如果还是失败 - Plan B

### Plan B1: 创建最小测试服务器

创建一个超级简单的服务器来测试 Zeabur 是否能正常运行：

```python
# test_server.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'status': 'ok', 'message': 'Minimal test server is running'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

修改 Zbfile：
```
default: python test_server.py
```

如果这个能运行，说明 Zeabur 本身没问题，问题在 api.py。

### Plan B2: 使用 Railway（Zeabur 替代品）

1. 前往 https://railway.app
2. 连接 GitHub 仓库
3. Railway 会自动检测 Procfile
4. 添加环境变量
5. 部署

### Plan B3: 使用 Render（免费）

1. 前往 https://render.com
2. 选择 "New Web Service"
3. 连接 GitHub 仓库
4. 构建命令：`pip install -r requirements.txt`
5. 启动命令：`gunicorn --bind 0.0.0.0:$PORT --timeout 600 api:app`
6. 添加环境变量

### Plan B4: 本地测试确认代码正确

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置环境变量（临时）
export REPLICATE_API_TOKEN="your_token_here"
export MESHY_API_KEY="your_key_here"
export PORT=8080

# 3. 运行服务器
gunicorn --bind 0.0.0.0:8080 --timeout 600 --workers 1 api:app

# 4. 测试
curl http://localhost:8080/
curl http://localhost:8080/api/health
```

如果本地能运行，说明代码没问题，是部署平台的问题。

---

## 🔧 常见问题解决

### 问题 1: "ModuleNotFoundError: No module named 'xxx'"
**解决**：检查 requirements.txt 是否包含该模块

### 问题 2: "Address already in use"
**解决**：Zeabur 的问题，通常重新部署即可

### 问题 3: 仍然看到 test_input.png
**解决**：
```bash
# 确认 main.py 已删除
ls -la *.py
# 应该只看到 api.py

# 确认已推送
git log --oneline -5
```

### 问题 4: "Worker timeout"
**解决**：已经在 gunicorn 设置了 600 秒超时，应该足够

---

## 📞 终极方案：简化部署

如果上述都不行，创建一个超级简化版本：

1. **只部署健康检查**（不包含 3D 生成功能）
2. **确认部署流程正常**
3. **逐步添加功能**

我可以帮你创建这个简化版本。

---

## 🎯 下一步行动

告诉我：
1. Zeabur 日志显示什么？（截图或复制关键部分）
2. 服务器状态是什么？（运行中/崩溃/错误）
3. 如果需要，我们切换到 Plan B 的哪一个？
