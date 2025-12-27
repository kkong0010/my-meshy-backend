from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import time
import uuid
import urllib3

# === 🛡️ 1. 禁用 SSL 警告 ===
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === 🛡️ 2. 强制清除代理 ===
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

app = Flask(__name__, static_folder='static')

# === 配置区域 ===
UPLOAD_FOLDER = 'static/uploads'
MODEL_FOLDER = 'static/models'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)

# === 🔑 读取 Key ===
API_KEY = None
try:
    with open("api_key.txt", "r") as f: API_KEY = f.read().strip()
except:
    try:
        with open("api_key", "r") as f: API_KEY = f.read().strip()
    except:
        print("❌ 找不到 Key 文件")
        exit()

BASE_URL = "https://api.tripo3d.ai/v2/openapi"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# === 🛡️ 通用网络请求保险箱 (用于非文件上传请求) ===
def safe_request(method, url, max_retries=10, **kwargs):
    for i in range(max_retries):
        try:
            kwargs['verify'] = False; kwargs['timeout'] = 60
            if method.lower() == 'post': response = requests.post(url, headers=HEADERS, **kwargs)
            else: response = requests.get(url, headers=HEADERS, **kwargs)
            return response
        except Exception as e:
            print(f"⚠️ 网络波动 ({i+1}/{max_retries}): {e}")
            time.sleep(2)
    raise Exception("连接失败")

def process_tripo_task(image_path):
    print(f"🚀 [后端] 处理: {image_path}")
    try:
        # 1. 上传 (⚡️ 修复版：每次重试都重新打开文件)
        token = None
        for i in range(5):
            try:
                # 关键修改：每次循环都重新 open，保证文件指针在开头
                with open(image_path, 'rb') as f:
                    files = {'file': f}
                    res = requests.post(f"{BASE_URL}/upload", headers=HEADERS, files=files, timeout=60, verify=False)
                    
                    if res.status_code == 200:
                        token = res.json()['data']['image_token']
                        print("✅ [后端] 上传成功")
                        break
                    else:
                        print(f"⚠️ 上传失败 ({res.status_code})，正在重试...")
            except Exception as e:
                print(f"⚠️ 上传网络波动 ({i+1}/5): {e}")
            time.sleep(2)
        
        if not token: raise Exception("图片上传最终失败，请检查网络")

        # 2. 创建任务
        payload = {"type": "image_to_model", "file": {"type": "png", "file_token": token}}
        res = safe_request('post', f"{BASE_URL}/task", json=payload)
        if res.status_code != 200: raise Exception(f"任务创建失败: {res.text}")
        
        task_id = res.json()['data']['task_id']
        print(f"✅ [后端] 任务ID: {task_id}")

        # 3. 轮询
        start = time.time()
        while time.time() - start < 600:
            res = safe_request('get', f"{BASE_URL}/task/{task_id}", max_retries=5)
            data = res.json()['data']
            status = data['status']
            print(f"⏳ [后端] 进度: {data.get('progress', 0)}%   ", end='\r')
            
            if status == 'success':
                out = data['output']
                return out.get('pbr_model') or out.get('model') or out.get('base_model')
            elif status in ['failed', 'cancelled']: raise Exception("任务失败")
            time.sleep(2)
            
    except Exception as e:
        print(f"\n❌ [后端] 出错: {e}")
        return None

@app.route('/')
def index(): return send_from_directory('.', 'index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    filename = str(uuid.uuid4()) + ".png"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    url = process_tripo_task(path)
    if url:
        local_name = f"model_{str(uuid.uuid4())}.glb"
        local_path = os.path.join(MODEL_FOLDER, local_name)
        try:
            res = safe_request('get', url, stream=True)
            with open(local_path, 'wb') as f:
                for chunk in res.iter_content(chunk_size=8192): f.write(chunk)
            return jsonify({'model_url': f"/{MODEL_FOLDER}/{local_name}"})
        except Exception as e: return jsonify({'error': str(e)}), 500
    return jsonify({'error': '生成失败'}), 500

if __name__ == '__main__':
    print("\n✅ 服务已启动 (上传修复版)")
    app.run(host='0.0.0.0', port=5000)