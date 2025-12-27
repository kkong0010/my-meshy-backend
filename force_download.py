import requests
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

# === 2. 你的任务 ID (直接锁定这个做好的任务) ===
TASK_ID = "3fba8af2-497c-4802-9771-6f1b296140fd"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

print(f"🔄 正在尝试重新连接任务: {TASK_ID} ...")

try:
    # 重新获取一个新鲜的下载链接
    response = requests.get(f"https://api.tripo3d.ai/v2/openapi/task/{TASK_ID}", headers=HEADERS)
    data = response.json()
    output = data.get('data', {}).get('output', {})
    
    # 优先下载高质量的 PBR 模型
    model_url = output.get('pbr_model') or output.get('model') or output.get('base_model')
    
    if model_url:
        print(f"⬇️ 链接获取成功！准备开始强力下载...")
        print("   (如果卡住请耐心等待，正在下载约 15MB 的文件)")
        
        # 使用 stream=True 模式，像流水一样一点点接，防止一口气噎死
        with requests.get(model_url, stream=True) as r:
            r.raise_for_status()
            with open("output_model.glb", "wb") as f:
                # 每次下载 8KB，积少成多
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
                    downloaded += len(chunk)
                    # 打印一个小点点表示还活着
                    if downloaded % (1024*1024) < 8192: # 每下载 1MB 打印一次
                        print(".", end="", flush=True)
                        
        print("\n\n🏆 终于成功了！文件已完整保存为: output_model.glb")
        print("👉 现在去双击打开它吧！")
    else:
        print("❌ 奇怪，服务器没返回下载链接。")
        
except Exception as e:
    print(f"\n❌ 依然报错: {e}")
    print("💡 备选方案：如果代码实在下载不下来，请把报错信息发给我。")