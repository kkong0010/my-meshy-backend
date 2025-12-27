import requests
import time
import os
import json

# ================= 配置区域 =================
# 自动寻找 Key 文件 (兼容 api_key 或 api_key.txt)
API_KEY_FILE = "api_key.txt"
if not os.path.exists(API_KEY_FILE) and os.path.exists("api_key"):
    API_KEY_FILE = "api_key"

try:
    with open(API_KEY_FILE, "r") as f:
        API_KEY = f.read().strip() # 读取并去除空格
    print(f"✅ 成功读取 API Key")
except FileNotFoundError:
    print(f"❌ 错误：找不到 api_key.txt 文件！")
    exit()

# Tripo V2 API 基础设置
BASE_URL = "https://api.tripo3d.ai/v2/openapi"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

def upload_image(file_path):
    """第一步：上传图片"""
    # 强制使用标准 upload 接口，不使用 sts
    url = f"{BASE_URL}/upload" 
    
    print(f"\n🚀 1. 正在上传图片: {file_path} ...")
    if not os.path.exists(file_path):
        print(f"❌ 找不到图片文件: {file_path}")
        return None

    try:
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url, headers=HEADERS, files=files)
        
        if response.status_code == 200:
            data = response.json()
            # 这里的 .get 是为了防止 key 不存在报错
            token = data.get('data', {}).get('image_token')
            if token:
                print(f"✅ 上传成功! Image Token 获取完毕")
                return token
            else:
                print(f"❌ 上传成功但没找到 Token，返回数据: {data}")
        else:
            print(f"❌ 上传失败 (状态码 {response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ 上传过程出错: {e}")
    return None

def create_task(image_token):
    """第二步：创建生成任务"""
    url = f"{BASE_URL}/task"
    
    payload = {
        "type": "image_to_model",
        "file": {
            "type": "png", 
            "file_token": image_token
        }
    }
    
    print("\n🔨 2. 正在向服务器发送生成指令...")
    response = requests.post(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        task_id = data.get('data', {}).get('task_id')
        print(f"✅ 任务创建成功! Task ID: {task_id}")
        return task_id
    else:
        print(f"❌ 创建任务失败: {response.text}")
        return None

def check_task(task_id):
    """第三步：轮询状态"""
    url = f"{BASE_URL}/task/{task_id}"
    print("\n⏳ 3. 开始轮询任务状态 (每 2 秒一次)...")
    
    start_time = time.time()
    while True:
        # 5分钟超时保护
        if time.time() - start_time > 300:
            print("❌ 超时：等待超过 5 分钟。")
            return None

        try:
            response = requests.get(url, headers=HEADERS)
            data = response.json()
            
            status = data.get('data', {}).get('status')
            progress = data.get('data', {}).get('progress', 0)
            
            if status == 'running' or status == 'queued':
                print(f"   ... 正在生成中 (进度: {progress}%)", end='\r')
            
            elif status == 'success':
                print(f"\n🎉 生成成功！进度: 100%")
                # 获取下载链接
                output = data.get('data', {}).get('output', {})
                # 优先找 model，没有的话找 base_model
                model_url = output.get('model') or output.get('base_model')
                return model_url
                
            elif status == 'failed' or status == 'cancelled':
                print(f"\n💀 任务失败，服务器返回: {data}")
                return None
            
            time.sleep(2) # 等待 2 秒
            
        except Exception as e:
            print(f"⚠️ 查询出错: {e}")
            time.sleep(2)

def download_model(url, filename="output_model.glb"):
    """第四步：下载结果"""
    print(f"\n⬇️ 4. 正在下载模型文件...")
    if not url:
        print("❌ 下载链接为空！")
        return

    try:
        res = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(res.content)
        print(f"🏆 大功告成！文件已保存为: {filename}")
        print("👉 提示：去文件夹里双击看看效果吧！")
    except Exception as e:
        print(f"❌ 下载写入文件出错: {e}")

# ================= 主程序入口 =================
if __name__ == "__main__":
    # 确认你的图片文件名
    input_image = "test_input.png" 
    
    token = upload_image(input_image)
    if token:
        task_id = create_task(token)
        if task_id:
            model_url = check_task(task_id)
            if model_url:
                download_model(model_url)
