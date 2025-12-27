import requests
import json
import os

# === 1. 读取 Key ===
try:
    with open("api_key.txt", "r") as f:
        API_KEY = f.read().strip()
except:
    try: 
        with open("api_key", "r") as f: API_KEY = f.read().strip()
    except: 
        print("❌ 找不到 Key 文件"); exit()

# === 2. 你的任务 ID (来自截图) ===
TASK_ID = "3fba8af2-497c-4802-9771-6f1b296140fd"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

print(f"🔍 正在去服务器查询任务: {TASK_ID} ...")

# === 3. 查询 ===
try:
    response = requests.get(f"https://api.tripo3d.ai/v2/openapi/task/{TASK_ID}", headers=HEADERS)
    data = response.json()
    
    # 打印出来让我们看看它到底长啥样
    # print("🔍 服务器返回的完整数据:", json.dumps(data, indent=2)) 
    
    status = data.get('data', {}).get('status')
    if status == 'success':
        output = data.get('data', {}).get('output', {})
        print(f"✅ 状态确认成功！发现以下输出文件: {list(output.keys())}")
        
        # 智能寻找下载链接 (不管它叫 model 还是 base_model 还是其他)
        model_url = output.get('model') or output.get('base_model') or output.get('pbr_model')
        
        # 如果还没找到，就找第一个是 http 开头的链接
        if not model_url:
            for k, v in output.items():
                if isinstance(v, str) and v.startswith("http") and ".glb" in v:
                    model_url = v
                    print(f"👉 自动匹配到链接: {k}")
                    break
        
        if model_url:
            print(f"⬇️ 正在下载: {model_url}")
            res = requests.get(model_url)
            with open("output_model.glb", "wb") as f:
                f.write(res.content)
            print("🏆 成功！文件已保存为: output_model.glb (快去双击看看！)")
        else:
            print("❌ 虽然成功了，但在 output 里没找到下载链接。请截图发给 Gemini。")
            print(json.dumps(output, indent=2))
            
    else:
        print(f"⚠️ 任务状态显示为: {status}")

except Exception as e:
    print(f"❌ 出错啦: {e}")