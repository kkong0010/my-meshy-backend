from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import time
import uuid
import urllib3
import mimetypes
import replicate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Clear proxy settings
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

app = Flask(__name__, static_folder='static')
# Enable CORS for all origins (required for deployed frontend)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# === Configuration ===
UPLOAD_FOLDER = 'static/uploads'
MODEL_FOLDER = 'static/models'

# Create folders safely (don't crash if fails)
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(MODEL_FOLDER, exist_ok=True)
    print(f"[SUCCESS] Created/verified folders: {UPLOAD_FOLDER}, {MODEL_FOLDER}")
except Exception as e:
    print(f"[WARNING] Could not create folders: {e}")
    print("[WARNING] Server will continue but may fail when saving files")

# === Read API Key (Environment Variable + File Fallback) ===
API_KEY = None
API_KEY_FILE = None

# Try environment variable first (for deployment)
API_KEY = os.environ.get('REPLICATE_API_TOKEN') or os.environ.get('REPLICATE_API_KEY')
if API_KEY:
    print("[SUCCESS] API Key loaded from environment variable")
else:
    # Fallback to file (for local development)
    for key_file in ["api_key.txt", "api_key"]:
        key_path = os.path.join(os.path.dirname(__file__), key_file)
        if os.path.exists(key_path):
            with open(key_path, "r") as f:
                API_KEY = f.read().strip()
            API_KEY_FILE = key_file
            print(f"[SUCCESS] API Key loaded from: {key_file}")
            break

if API_KEY:
    # Print masked key for verification
    key_prefix = API_KEY[:4] if len(API_KEY) >= 4 else "***"
    masked_key = f"{API_KEY[:8]}...{API_KEY[-6:]}" if len(API_KEY) > 14 else "***"
    print(f"[KEY PREFIX] First 4 chars: {key_prefix}")
    print(f"[KEY PREVIEW] {masked_key}")
else:
    print("[WARNING] API Key not found - set REPLICATE_API_TOKEN environment variable")
    print("[WARNING] Server will start but generation will fail without API key")

BASE_URL = "https://api.tripo3d.ai/v2/openapi"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# === Network Request with Retry (Enhanced) ===
def safe_request(method, url, max_retries=5, **kwargs):
    """Network request with retry mechanism - Enhanced error logging"""
    for i in range(max_retries):
        try:
            kwargs['verify'] = False
            kwargs['timeout'] = kwargs.get('timeout', 120)  # Increase to 120s

            print(f"[REQUEST] [{method.upper()}] {url}")

            if method.lower() == 'post':
                response = requests.post(url, headers=HEADERS, **kwargs)
            else:
                response = requests.get(url, headers=HEADERS, **kwargs)

            print(f"[RESPONSE] Status code: {response.status_code}")

            # Log response details
            if response.status_code != 200:
                print(f"[WARNING] Non-200 response: {response.text[:200]}")

            return response

        except requests.exceptions.Timeout as e:
            print(f"[TIMEOUT] Attempt ({i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                time.sleep(3)
            else:
                raise Exception(f"Request timeout after {max_retries} retries")

        except requests.exceptions.ConnectionError as e:
            print(f"[CONNECTION ERROR] Attempt ({i+1}/{max_retries}): {e}")
            if i < max_retries - 1:
                time.sleep(3)
            else:
                raise Exception(f"Network connection failed: {str(e)}")

        except Exception as e:
            print(f"[ERROR] Unknown error ({i+1}/{max_retries}): {type(e).__name__} - {e}")
            if i < max_retries - 1:
                time.sleep(2)
            else:
                raise
    return None

def upload_image_to_tripo(file_path):
    """Upload image to Tripo API"""
    print(f"[UPLOAD] Uploading image: {file_path}")

    # Detect file type
    mime_type = mimetypes.guess_type(file_path)[0]
    if mime_type:
        file_type = mime_type.split('/')[-1]  # 'jpeg', 'png', 'webp'
    else:
        file_type = 'png'  # default

    # Retry upload
    for i in range(5):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, mime_type)}
                response = requests.post(
                    f"{BASE_URL}/upload",
                    headers=HEADERS,
                    files=files,
                    timeout=60,
                    verify=False
                )

                if response.status_code == 200:
                    data = response.json()
                    token = data.get('data', {}).get('image_token')
                    if token:
                        print(f"[SUCCESS] Upload successful, Token: {token[:20]}...")
                        return token, file_type
                    else:
                        print(f"[WARNING] Unexpected response format: {data}")
                else:
                    print(f"[WARNING] Upload failed ({response.status_code}): {response.text}")

        except Exception as e:
            print(f"[WARNING] Upload exception ({i+1}/5): {e}")

        time.sleep(2)

    raise Exception("Image upload failed after 5 retries")

def create_tripo_task(image_token, file_type, options=None):
    """Create Tripo 3D generation task - Anime Head Specialized v2.0"""
    options = options or {}

    # Core: Ultimate Anime Figurine Style Guide (STRICT COMPETITION COMPLIANCE)
    # Real Photo Input → Anime Style Head Model Output
    anime_figurine_style_guide = (
        "[ULTIMATE ANIME FIGURINE BUST] "
        "Highly stylized anime bust portrait, head and shoulders, cel shaded style, "
        "clean lines, vibrant flat colors, smooth pvc figure texture, "
        "no photorealistic details, masterpiece, best quality, 3d render stylized"
    )
    print(f"\n{anime_figurine_style_guide}\n")

    payload = {
        "type": "image_to_model",
        "file": {
            "type": file_type,
            "file_token": image_token
        }
    }

    # Model version: Use v3.0 for high-end quality
    payload['model_version'] = options.get('model_version', 'v3.0-20250812')

    # Force enable PBR materials (anime rendering effect)
    payload['pbr'] = True

    # Texture quality: Use detailed for better anime details
    payload['texture_quality'] = options.get('texture_quality', 'detailed')

    # Face optimization: 8000 faces for head detail
    payload['face_limit'] = options.get('face_limit', 8000)

    # Enable image auto-optimization (enhance anime features)
    payload['enable_image_autofix'] = True

    # Texture alignment: Keep original style (anime feel)
    payload['texture_alignment'] = 'original_image'

    # Geometry quality: Use detailed mode (v3.0+ feature)
    if payload['model_version'] >= 'v3.0':
        payload['geometry_quality'] = 'detailed'

    # Auto-rotate to align with original image (keep head forward)
    payload['orientation'] = 'align_image'

    # Auto-scale to real size
    payload['auto_size'] = False  # Keep original proportions

    print(f"[TASK] ========================================")
    print(f"[TASK] Creating Anime Head Modeling Task")
    print(f"[TASK] ========================================")
    print(f"[PARAMS] Task parameters:")
    for key, value in payload.items():
        if key != 'file':
            print(f"   - {key}: {value}")
    print(f"[TASK] ========================================\n")

    try:
        # Extend timeout to 60s
        response = safe_request('post', f"{BASE_URL}/task", json=payload, timeout=60)

        if not response:
            raise Exception("Server not responding! Check network or API key")

        print(f"[API RESPONSE] Preview: {response.text[:300]}...\n")

        if response.status_code == 200:
            data = response.json()
            task_id = data.get('data', {}).get('task_id')
            if task_id:
                print(f"[SUCCESS] Task created successfully!")
                print(f"[TASK ID] {task_id}")
                print(f"[STATUS] Preparing to start 3D conversion...\n")
                return task_id
            else:
                raise Exception(f"Unexpected API response data: {data}")
        elif response.status_code == 401:
            raise Exception("Invalid API Key! Please check your API key")
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded! Please try again later")
        elif response.status_code == 403:
            raise Exception("Insufficient balance! Please check your account")
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('message', response.text)
            raise Exception(f"Task creation failed (Status {response.status_code}): {error_msg}")

    except requests.exceptions.Timeout:
        raise Exception("Request timeout! Network connection is slow")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Cannot connect to server! Check network connection\nDetails: {str(e)[:100]}")
    except Exception as e:
        print(f"[FAILURE] Task creation failed:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}\n")
        raise

def poll_task_status(task_id, timeout=600):
    """Poll task status"""
    print(f"[POLLING] Starting task polling: {task_id}")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = safe_request('get', f"{BASE_URL}/task/{task_id}", max_retries=3)

            if not response:
                continue

            data = response.json()
            task_data = data.get('data', {})
            status = task_data.get('status')
            progress = task_data.get('progress', 0)

            print(f"   Progress: {progress}% - Status: {status}", end='\r')

            if status == 'success':
                print(f"\n[SUCCESS] Generation completed!")
                output = task_data.get('output', {})
                # Priority: PBR model > regular model > base model
                model_url = (output.get('pbr_model') or
                           output.get('model') or
                           output.get('base_model'))
                return model_url

            elif status in ['failed', 'cancelled']:
                raise Exception(f"Task failed: {status}")

        except Exception as e:
            print(f"\n[WARNING] Polling error: {e}")

        time.sleep(2)

    raise Exception("Task timeout")

def download_model_file(url, local_path):
    """Download model file"""
    print(f"[DOWNLOAD] Downloading model: {url[:50]}...")

    response = safe_request('get', url, stream=True, timeout=180)

    if response and response.status_code == 200:
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"[SUCCESS] Download complete: {local_path}")
        return True
    else:
        raise Exception("Model download failed")

def apply_anime_filter(image_path):
    """Stage 1: Apply AI anime filter using Replicate SDXL

    Converts real photo → anime-styled 2D image before 3D modeling
    This solves the uncanny valley problem by pre-stylizing the input
    """
    print(f"\n{'='*60}")
    print(f"[STAGE 1/2] AI ANIME FILTER - Real Photo → Anime Drawing")
    print(f"{'='*60}")
    print(f"[INPUT] Original photo: {image_path}")

    # Get Replicate API token from environment
    replicate_token = os.getenv('REPLICATE_API_TOKEN')
    if not replicate_token:
        print("[ERROR] REPLICATE_API_TOKEN not found in environment variables")
        raise Exception("REPLICATE_API_TOKEN environment variable is required. Please set it in Zeabur dashboard.")

    # Configure Replicate client
    os.environ['REPLICATE_API_TOKEN'] = replicate_token

    try:
        # Open image file
        with open(image_path, 'rb') as img_file:
            print(f"[FACE-TO-MANY 3D] Running Face-to-Many Model with 3D Style...")
            print(f"[FACE-TO-MANY 3D] Model: fofr/face-to-many (Identity-Preserving 3D Avatar)")
            print(f"[FACE-TO-MANY 3D] Style: 3D | Instant ID Strength: 1.0 (100% Face Lock)")

            # Run Face-to-Many with Geometry-Optimized Output for Clean 3D Reconstruction
            output = replicate.run(
                "fofr/face-to-many:a07f252abbbd832009640b27f063ea52d87d7a23a185ca165bec23b5adc8deaf",
                input={
                    "image": img_file,
                    "style": "3D",  # Magic switch for Apple/Memoji look
                    "prompt": "pop mart style, apple emoji style, cute 3d character, blind box toy, full body view, standing character, wearing cute shoes, chibi proportions, big head small body, arms at sides, A-pose, simple legs, matte clay material, soft finish, smooth surface, pastel colors, clean geometry, 3d render, octane render, soft studio lighting, frontal view, symmetrical, white background, 4k ultra-detailed, sharp focus, 8k resolution, extremely high resolution, professional 3d sculpture texture, hyper-realistic surface detail, intricate textures, masterpiece, high-end designer toy, smooth porcelain finish, ambient occlusion, ray tracing, clean edges, high contrast, solid silhouette, studio background, water-tight mesh, clean topology, smooth surfaces, manifold geometry",
                    "negative_prompt": "lowres, artifacts, messy hair, blurred, low poly, distorted, bad anatomy, noise, grainy, dark shadows, harsh lighting, deformed, text, watermark, logo, holes, floating pixels, disconnected parts, thin mesh, jagged edges, messy background",
                    "prompt_strength": 4.5,
                    "denoising_strength": 0.5,  # More conservative for cleaner edges and less visual noise
                    "instant_id_strength": 0.75,  # Maintains identity but keeps it cute
                    "num_outputs": 1,
                    "output_format": "png"  # High quality for Refine stage
                }
            )

            # Handle both list and single object outputs
            if output:
                if isinstance(output, list):
                    # If it's a list (old behavior), take the first item
                    anime_image_url = str(output[0])
                else:
                    # If it's a single object (new behavior), use it directly
                    anime_image_url = str(output)

                print(f"[SUCCESS] Anime filter applied!")
                print(f"[OUTPUT] 2D Anime Image URL: {anime_image_url[:60]}...")
                print(f"{'='*60}\n")
                return anime_image_url
            else:
                raise Exception("No output from Replicate SDXL")

    except Exception as e:
        print(f"[ERROR] Anime filter failed: {e}")
        raise Exception(f"Stage 1 (Anime Filter) failed: {str(e)}")

# === API Routes ===

@app.route('/')
def index():
    """Root endpoint - Shows server is alive"""
    return jsonify({
        'status': 'running',
        'version': 'v2.0-no-startup-tests',
        'message': 'Server Active v2 - NO automatic API calls on startup',
        'endpoints': {
            'health': '/api/health',
            'generate': '/api/generate (POST)',
            'static': '/static/<path>'
        },
        'api_keys': {
            'replicate': bool(os.getenv('REPLICATE_API_TOKEN')),
            'meshy': bool(os.getenv('MESHY_API_KEY'))
        },
        'note': 'API calls ONLY happen when user clicks Generate button'
    })

@app.route('/api/generate', methods=['POST'])
def generate_model():
    """2-STAGE PIPELINE: Real Photo → Anime Drawing → 3D Model

    Stage 1: Apply anime filter using Replicate SDXL (img2img)
    Stage 2: Generate 3D model from anime drawing using Tripo
    """
    try:
        # Get file count (multi-image support)
        file_count = int(request.form.get('file_count', 1))
        print(f"\n{'='*70}")
        print(f"[2-STAGE PIPELINE] Starting Real-to-Anime-to-3D Generation")
        print(f"{'='*70}")
        print(f"[INPUT] Received {file_count} image(s)")

        uploaded_paths = []

        # Process all uploaded images
        for i in range(file_count):
            file_key = f'file{i}'
            if file_key not in request.files:
                print(f"[WARNING] {file_key} not found in request")
                continue

            file = request.files[file_key]
            if file.filename == '':
                continue

            # Save uploaded image
            ext = os.path.splitext(file.filename)[1] or '.png'
            filename = f"{uuid.uuid4()}{ext}"
            upload_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(upload_path)
            uploaded_paths.append(upload_path)
            print(f"[FILE] File {i+1} saved: {upload_path}")

        if len(uploaded_paths) == 0:
            return jsonify({'error': 'No valid images uploaded'}), 400

        # Get generation options
        options = {
            'model_version': request.form.get('model_version', 'v2.5-20250123'),
            'pbr': request.form.get('pbr', 'true').lower() == 'true',
            'texture_quality': request.form.get('texture_quality', 'standard'),
        }

        # Use first image as primary
        print(f"[PRIMARY IMAGE] Using {uploaded_paths[0]} as primary")

        # ============================================
        # STAGE 1: Apply Anime Filter (Real → 3D Avatar)
        # ============================================
        anime_image_url = apply_anime_filter(uploaded_paths[0])

        # ============================================
        # RATE LIMIT SAFETY: Cool down between API calls
        # ============================================
        print(f"\n{'='*60}")
        print(f"[RATE LIMIT SAFETY] Cooling down for 5 seconds...")
        print(f"[RATE LIMIT SAFETY] Preventing Replicate 429 burst limit error")
        print(f"{'='*60}", flush=True)
        time.sleep(5)  # Wait 5 seconds to clear the burst limit

        # ============================================
        # STAGE 2: Generate 3D Model with Meshy AI (Server-Side Polling!)
        # ============================================
        print(f"\n{'='*60}")
        print(f"[STAGE 2/2] MESHY AI - 3D Avatar → 3D Mesh")
        print(f"{'='*60}")

        # 1. Configuration - Use environment variable
        MESHY_API_KEY = os.environ.get('MESHY_API_KEY')
        if not MESHY_API_KEY:
            print("[ERROR] MESHY_API_KEY not found in environment variables", flush=True)
            raise Exception("MESHY_API_KEY environment variable is required. Please set it in Zeabur dashboard.")

        MESHY_HEADERS = {'Authorization': f'Bearer {MESHY_API_KEY}'}

        print(f"🚀 Submitting to Meshy (Refine Mode - 4K ULTRA QUALITY)...", flush=True)
        print(f"⚠️  NOTE: 4K Refine mode takes ~3-7 minutes for maximum detail", flush=True)

        # 2. Submit Task (CRITICAL: Refine = 4K Quality & Maximum Detail)
        payload = {
            "image_url": anime_image_url,
            "enable_pbr": True,  # CRITICAL: Enables 4K PBR textures with realistic light interaction
            "mode": "refine"  # CRITICAL: Force 4K Refine Mode for highest possible detail
        }

        try:
            response = requests.post(
                "https://api.meshy.ai/v1/image-to-3d",
                headers=MESHY_HEADERS,
                json=payload
            )
            response.raise_for_status()
            result_id = response.json()["result"]
        except Exception as e:
            print(f"❌ Meshy Submit Error: {e}", flush=True)
            raise Exception(f"Meshy submission failed: {str(e)}")

        print(f"Task ID: {result_id}. Polling...", flush=True)

        # 3. Poll for Completion (Extended for 4K Refine Mode)
        for i in range(200):  # Timeout after 400s (6-7 minutes for 4K refine mode)
            time.sleep(2)
            check_resp = requests.get(
                f"https://api.meshy.ai/v1/image-to-3d/{result_id}",
                headers=MESHY_HEADERS
            )
            status_data = check_resp.json()
            status = status_data.get("status")

            print(f"[POLL {i+1}/60] Status: {status}", flush=True)

            if status == "SUCCEEDED":
                print("✅ Meshy Success!", flush=True)
                model_url = status_data["model_urls"]["glb"]

                # Download the GLB file
                model_filename = f"model_{uuid.uuid4()}.glb"
                model_path = os.path.join(MODEL_FOLDER, model_filename)

                print(f"[MESHY] Downloading model to: {model_path}")
                model_response = requests.get(model_url, timeout=60, verify=False)
                if model_response.status_code == 200:
                    with open(model_path, 'wb') as f:
                        f.write(model_response.content)
                    print(f"[SUCCESS] Model saved: {model_path}")
                else:
                    raise Exception(f"Failed to download model: HTTP {model_response.status_code}")

                print(f"\n{'='*70}")
                print(f"[COMPLETE] 2-Stage Pipeline Finished Successfully!")
                print(f"[COMPLETE] Total time: ~3-7 minutes (Face-to-Many + Meshy 4K Refine)")
                print(f"[COMPLETE] Quality: 4K PBR Textures | Maximum Detail")
                print(f"{'='*70}\n")

                # Return frontend-accessible path
                return jsonify({
                    'success': True,
                    'model_url': f"/static/models/{model_filename}",
                    'anime_image_url': anime_image_url
                })

            elif status in ["FAILED", "EXPIRED"]:
                raise Exception(f"Meshy task failed with status: {status}")

        raise Exception("Meshy timeout after 400 seconds (4K refine mode)")

    except Exception as e:
        print(f"[ERROR] Generation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files with proper CORS headers"""
    try:
        # Determine mimetype for GLB files
        mimetype = 'model/gltf-binary' if path.endswith('.glb') else None
        response = send_from_directory('static', path, mimetype=mimetype)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
    except Exception as e:
        print(f"[ERROR] Static file error: {e}")
        return jsonify({'error': f'File not found: {path}'}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check - v2"""
    return jsonify({
        'status': 'Server Active v2',
        'version': 'v2.0-no-startup-tests',
        'replicate_api_token': 'loaded' if os.getenv('REPLICATE_API_TOKEN') else 'missing',
        'meshy_api_key': 'loaded' if os.getenv('MESHY_API_KEY') else 'missing',
        'note': 'NO startup tests - API calls only on user request'
    })

if __name__ == '__main__':
    # Get port from environment variable (Zeabur sets this)
    port = int(os.environ.get('PORT', 8080))

    print("=" * 60)
    print("[STARTING] Tripo 3D API Server v2.0-no-startup-tests")
    print("=" * 60)
    print(f"[PORT] {port}")
    print(f"[HOST] 0.0.0.0")
    print(f"[REPLICATE_API_TOKEN] {'✓ Loaded' if os.getenv('REPLICATE_API_TOKEN') else '⚠ Not set (will fail on generate)'}")
    print(f"[MESHY_API_KEY] {'✓ Loaded' if os.getenv('MESHY_API_KEY') else '⚠ Not set (will fail on generate)'}")
    print("[IMPORTANT] NO STARTUP TESTS - Server will NOT call any APIs on startup")
    print("[IMPORTANT] API calls ONLY happen when user clicks Generate button")
    print("=" * 60)

    # Production mode for Zeabur (no debug mode in production)
    # Server will start even without API keys - errors only happen when user clicks Generate
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"[FATAL] Server failed to start: {e}")
        # Don't exit - let container restart
