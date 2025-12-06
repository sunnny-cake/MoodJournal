import streamlit as st
import base64
import os
import json
from datetime import datetime, date
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random
import uuid
import requests

# 火山方舟AI导入（可选，如果未安装则使用降级方案）
try:
    from volcenginesdkarkruntime import Ark
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# 支持从.env文件加载环境变量（推荐方式）
try:
    from dotenv import load_dotenv
    load_dotenv()  # 自动加载项目根目录下的.env文件
except ImportError:
    # 如果没有安装python-dotenv，跳过（不影响功能）
    pass

# Supabase支持（可选，如果配置了环境变量则使用云数据库）
try:
    from supabase_config import (
        get_supabase_client,
        upload_image_to_supabase,
        upload_file_to_supabase,
        load_journals_from_supabase,
        save_journal_to_supabase,
        update_journal_in_supabase,
        delete_journal_from_supabase,
        search_journals_in_supabase,
        filter_journals_by_weather
    )
    SUPABASE_AVAILABLE = get_supabase_client() is not None
except ImportError:
    SUPABASE_AVAILABLE = False
except Exception:
    SUPABASE_AVAILABLE = False

# ==========================================
# 1. 配置与常量
# ==========================================
st.set_page_config(
    page_title="MoodJournal - 情绪手帐", 
    layout="wide", 
    initial_sidebar_state="expanded",  # 改为展开状态，方便看到所有选项
    menu_items=None
)

# 强制显示侧边栏（如果被隐藏）
# 使用JavaScript确保侧边栏始终可见
st.markdown("""
<script>
// 确保侧边栏始终可见
window.addEventListener('load', function() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        sidebar.style.visibility = 'visible';
        sidebar.style.display = 'block';
        sidebar.style.zIndex = '999';
    }
    
    // 确保侧边栏按钮可见
    const sidebarButton = document.querySelector('[data-testid="stHeader"] button');
    if (sidebarButton) {
        sidebarButton.style.visibility = 'visible';
        sidebarButton.style.display = 'block';
        sidebarButton.style.zIndex = '1000';
    }
});
</script>
""", unsafe_allow_html=True)

# 路径配置
DATA_DIR = "data"
JOURNALS_FILE = os.path.join(DATA_DIR, "journals.json")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
bg_path = "assets/bg_rain.jpg"
icon_path = "assets/flower_icon.png"
fog_path = "assets/fog_overlay.png"

# 创建必要的目录
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# ==========================================
# 2. 数据存储函数（支持Supabase和本地文件）
# ==========================================
def load_journals():
    """加载所有日记条目（优先使用Supabase，降级到本地文件）"""
    if SUPABASE_AVAILABLE:
        try:
            journals = load_journals_from_supabase()
            # 转换格式以兼容现有代码（将URL转换为路径格式）
            for journal in journals:
                if "journal_image_url" in journal:
                    journal["journal_image_path"] = journal["journal_image_url"]
                if "image_paths" in journal and isinstance(journal["image_paths"], list):
                    # image_paths已经是URL数组，保持原样
                    pass
            return journals
        except Exception as e:
            st.warning(f"⚠️ Supabase加载失败，使用本地文件：{str(e)}")
    
    # 降级到本地文件
    if os.path.exists(JOURNALS_FILE):
        try:
            with open(JOURNALS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_journals(journals):
    """保存日记条目（兼容函数，实际使用save_journal）"""
    # 这个函数主要用于向后兼容，实际保存使用save_journal函数
    if SUPABASE_AVAILABLE:
        # 如果使用Supabase，这个函数不应该被调用
        # 因为每个条目应该单独保存
        pass
    else:
        # 本地文件模式
        with open(JOURNALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(journals, f, ensure_ascii=False, indent=2)

def save_journal(journal_entry):
    """保存单个日记条目（新增，支持Supabase和本地）"""
    if SUPABASE_AVAILABLE:
        try:
            # 准备Supabase格式的数据
            supabase_data = {
                "date": journal_entry["date"],
                "weather": journal_entry["weather"],
                "text": journal_entry["text"],
                "image_paths": journal_entry.get("image_paths", []),
                "journal_image_url": journal_entry.get("journal_image_path") or journal_entry.get("journal_image_url")
            }
            journal_id = save_journal_to_supabase(supabase_data)
            if journal_id:
                journal_entry["id"] = journal_id
                return True
            return False
        except Exception as e:
            st.warning(f"⚠️ Supabase保存失败，使用本地文件：{str(e)}")
    
    # 降级到本地文件
    journals = load_journals()
    journals.append(journal_entry)
    with open(JOURNALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(journals, f, ensure_ascii=False, indent=2)
    return True

def save_image(uploaded_file):
    """保存上传的图片（优先使用Supabase Storage，降级到本地文件）"""
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(uploaded_file.name)[1]
    
    if SUPABASE_AVAILABLE:
        try:
            # 上传到Supabase Storage
            file_bytes = uploaded_file.getbuffer()
            filename = f"{file_id}{file_ext}"
            url = upload_file_to_supabase(file_bytes, filename, folder="uploads")
            if url:
                return url  # 返回URL而不是路径
        except Exception as e:
            st.warning(f"⚠️ Supabase上传失败，使用本地文件：{str(e)}")
    
    # 降级到本地文件
    file_path = os.path.join(IMAGES_DIR, f"{file_id}{file_ext}")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def load_image_from_path_or_url(path_or_url):
    """
    从本地路径或URL加载图片
    支持本地文件路径和HTTP/HTTPS URL
    
    Args:
        path_or_url: 本地文件路径或URL
    
    Returns:
        PIL Image对象，失败返回None
    """
    try:
        # 判断是URL还是本地路径
        if path_or_url.startswith(('http://', 'https://')):
            # 从URL加载
            response = requests.get(path_or_url, timeout=30)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            else:
                return None
        else:
            # 从本地路径加载
            if os.path.exists(path_or_url):
                return Image.open(path_or_url)
            else:
                return None
    except Exception as e:
        print(f"加载图片失败 ({path_or_url}): {e}")
        return None

# ==========================================
# 3. 图片处理函数（Shoegaze/Dreamcore风格）
# ==========================================
def apply_dreamcore_effects(img, intensity=0.7):
    """
    应用Dreamcore效果：模糊、滤镜、水汽感
    """
    # 转换为RGBA以便处理透明度
    img = img.convert("RGBA")
    
    # 1. 轻微模糊（失焦效果）
    blur_radius = int(3 * intensity)
    if blur_radius > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    # 2. 色调调整（冷色调，增加朦胧感）
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(0.8)  # 降低饱和度
    
    # 3. 亮度调整（略微降低）
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(0.9)
    
    # 4. 添加半透明层（水汽感）
    overlay = Image.new("RGBA", img.size, (200, 220, 255, int(30 * intensity)))
    img = Image.alpha_composite(img, overlay)
    
    return img

# ==========================================
# 4. AI生图相关函数
# ==========================================
def generate_ai_prompt(text, date_str, weather):
    """
    根据用户输入生成Dreamcore风格的AI生图prompt
    """
    # 基础Dreamcore风格关键词
    dreamcore_keywords = [
        "dreamcore aesthetic", "shoegaze atmosphere", "hazy and ethereal",
        "soft focus", "blurred bokeh lights", "rainy window", "nostalgic mood",
        "pastel colors", "vaporwave vibes", "memory fragments", "emotional atmosphere",
        "watery reflections", "translucent layers", "non-linear composition"
    ]
    
    # 根据天气调整氛围
    weather_moods = {
        "☀️ 晴天": "warm sunlight filtering through, golden hour glow, cheerful brightness",
        "⛅ 多云": "soft diffused light, gentle shadows, peaceful overcast sky",
        "🌧️ 雨天": "raindrops on glass, blurred city lights, melancholic rainy atmosphere",
        "❄️ 雪天": "snowflakes falling, cold blue tones, serene winter scene",
        "🌫️ 雾天": "thick fog, mysterious atmosphere, obscured distant views",
        "🌙 夜晚": "night city lights, dark moody tones, nocturnal dreamscape"
    }
    
    weather_mood = weather_moods.get(weather, "dreamy atmospheric")
    
    # 根据用户文字提取情绪关键词
    emotion_keywords = ""
    if text:
        # 简单的情感关键词提取（可以根据需要扩展）
        positive_words = ["开心", "快乐", "幸福", "美好", "温暖", "喜欢", "爱"]
        negative_words = ["难过", "悲伤", "孤独", "疲惫", "焦虑", "担心"]
        
        text_lower = text.lower()
        if any(word in text for word in positive_words):
            emotion_keywords = "warm and joyful, uplifting mood, positive energy"
        elif any(word in text for word in negative_words):
            emotion_keywords = "melancholic and introspective, soft sadness, contemplative mood"
        else:
            emotion_keywords = "peaceful and reflective, calm atmosphere, gentle emotions"
    
    # 组合prompt - 明确要求纯背景，不包含文字
    prompt_parts = [
        "A dreamcore aesthetic journal page background,",
        weather_mood + ",",
        emotion_keywords + "," if emotion_keywords else "",
        "featuring " + ", ".join(dreamcore_keywords[:5]) + ",",
        "vertical composition, soft pastel color palette,",
        "paper texture overlay, artistic journal style,",
        "NO TEXT, NO WORDS, NO LETTERS, pure background only,",  # 明确禁止文字
        "suitable for handwritten text overlay, abstract decorative elements only"
    ]
    
    prompt = " ".join([p for p in prompt_parts if p])
    
    # 如果用户有具体文字描述，只提取情绪和氛围，不直接加入文字内容
    if text and len(text) < 50:  # 短文本可以提取情绪
        # 只提取情绪关键词，不直接使用文字内容
        prompt += f", mood: {text[:20]}"  # 只取前20个字符作为情绪参考
    
    return prompt

def generate_ai_background(prompt, base_width=1200, base_height=1600, show_error=True):
    """
    使用火山方舟AI生成背景图片
    返回PIL Image对象，失败时返回None
    
    Args:
        prompt: 生图提示词
        base_width: 图片宽度
        base_height: 图片高度
        show_error: 是否显示错误信息（默认True，便于调试）
    """
    if not AI_AVAILABLE:
        if show_error:
            st.warning("⚠️ AI功能不可用：未安装 volcengine-python-sdk[ark]，请运行 `pip install 'volcengine-python-sdk[ark]'`")
        return None
    
    api_key = os.getenv('ARK_API_KEY')
    if not api_key:
        if show_error:
            st.warning("⚠️ AI功能不可用：未设置 ARK_API_KEY 环境变量。请在 .env 文件中设置，或使用系统环境变量。")
        return None
    
    try:
        # 初始化客户端
        client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=api_key,
        )
        
        # 调用生图API
        with st.spinner("🎨 AI正在生成背景图..."):
            imagesResponse = client.images.generate(
                model="doubao-seedream-4-5-251128",
                prompt=prompt,
                size="2K",  # 2K分辨率，适合作为背景
                response_format="url",
                watermark=False
            )
        
        # 获取图片URL并下载
        if imagesResponse.data and len(imagesResponse.data) > 0:
            image_url = imagesResponse.data[0].url
            
            # 下载图片
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                # 转换为PIL Image
                img = Image.open(BytesIO(response.content))
                
                # 调整尺寸以匹配手账页面
                img = img.resize((base_width, base_height), Image.Resampling.LANCZOS)
                
                st.success("✨ AI背景生成成功！")
                return img
            else:
                if show_error:
                    st.error(f"❌ 图片下载失败：HTTP {response.status_code}")
                return None
        else:
            if show_error:
                st.error("❌ AI生图返回为空，请检查API响应")
            return None
            
    except Exception as e:
        # 显示详细错误信息
        if show_error:
            error_msg = str(e)
            st.error(f"❌ AI生图失败：{error_msg}")
            # 如果是API相关错误，提供更多提示
            if "api_key" in error_msg.lower() or "auth" in error_msg.lower():
                st.info("💡 提示：请检查 API 密钥是否正确，或访问 https://console.volcengine.com/ark/region:ark+cn-beijing/apikey 获取新密钥")
            elif "model" in error_msg.lower():
                st.info("💡 提示：请检查模型ID是否正确：doubao-seedream-4-5-251128")
        return None

# ==========================================
# 5. 手帐生成函数
# ==========================================
def create_journal_page(images, text, date_str, weather, base_width=1200, base_height=1600, use_ai=True):
    """
    生成手帐页面
    风格：Shoegaze/Dreamcore - 失焦、朦胧、半透明、非线性排版
    
    Args:
        images: 用户上传的图片列表
        text: 用户输入的文本
        date_str: 日期字符串
        weather: 天气
        base_width: 基础宽度
        base_height: 基础高度
        use_ai: 是否使用AI生成背景（默认True）
    """
    # 尝试使用AI生成背景
    ai_background = None
    if use_ai:
        try:
            prompt = generate_ai_prompt(text, date_str, weather)
            # 显示生成的prompt（调试用，可选）
            # st.info(f"🎨 AI Prompt: {prompt[:100]}...")
            ai_background = generate_ai_background(prompt, base_width, base_height, show_error=True)
        except Exception as e:
            # AI失败时显示错误并降级
            st.warning(f"⚠️ AI生图异常，使用默认背景：{str(e)}")
            ai_background = None
    
    # 创建底图
    if ai_background:
        # 使用AI生成的背景作为底图
        base_img = ai_background.convert("RGBA")
        
        # 添加轻微的纸质纹理叠加（保持手账感）
        paper_overlay = Image.new("RGBA", (base_width, base_height), (245, 240, 235, 30))
        base_img = Image.alpha_composite(base_img, paper_overlay)
    else:
        # 降级方案：使用默认纸质纹理
        if use_ai:
            # 只在尝试使用AI但失败时显示提示（避免每次都显示）
            pass  # 错误信息已在 generate_ai_background 中显示
        base_img = Image.new("RGB", (base_width, base_height), (245, 240, 235))
        
        # 添加微妙的纹理（模拟纸张）
        draw = ImageDraw.Draw(base_img)
        for _ in range(1000):
            x = random.randint(0, base_width)
            y = random.randint(0, base_height)
            gray = random.randint(240, 250)
            draw.point((x, y), fill=(gray, gray-5, gray-10))
        
        # 如果有背景雨图，作为底层氛围
        if os.path.exists(bg_path):
            try:
                bg = Image.open(bg_path).convert("RGBA")
                bg = bg.resize((base_width, base_height), Image.Resampling.LANCZOS)
                # 非常低的透明度，作为氛围
                bg_alpha = bg.split()[3]
                bg_alpha = bg_alpha.point(lambda x: int(x * 0.15))
                bg.putalpha(bg_alpha)
                base_img = Image.alpha_composite(base_img.convert("RGBA"), bg).convert("RGB")
            except:
                pass
        
        # 转换为RGBA以便后续合成
        if base_img.mode != "RGBA":
            base_img = base_img.convert("RGBA")
    
    # 处理并放置图片（1-3张，非线性排版）
    processed_images = []
    for img_path in images[:3]:  # 最多3张
        img = load_image_from_path_or_url(img_path)
        if img:
            try:
                img = img.convert("RGBA")
                
                # 应用Dreamcore效果
                img = apply_dreamcore_effects(img, intensity=0.6)
                
                # 随机尺寸（但保持比例）- 移动端优化
                max_size = min(base_width, base_height) // 2.5
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                processed_images.append(img)
            except Exception as e:
                print(f"处理图片失败: {e}")
                continue
    
    # 非线性排版：随机位置和角度
    positions = []
    for i, img in enumerate(processed_images):
        # 计算可用区域（避免重叠）- 移动端优化边距
        margin = int(base_width * 0.1)  # 响应式边距
        x_range = (margin, base_width - img.width - margin)
        y_range = (margin, base_height - img.height - margin)
        
        # 尝试找到一个不重叠的位置
        max_attempts = 50
        for _ in range(max_attempts):
            x = random.randint(*x_range)
            y = random.randint(*y_range)
            
            # 检查是否与已有位置重叠
            overlap = False
            for px, py, pw, ph in positions:
                if not (x + img.width < px or x > px + pw or y + img.height < py or y > py + ph):
                    overlap = True
                    break
            
            if not overlap:
                positions.append((x, y, img.width, img.height))
                break
        else:
            # 如果找不到不重叠的位置，使用默认位置
            x = margin + i * (base_width - 2 * margin) // len(processed_images)
            y = margin + random.randint(0, base_height // 3)
            positions.append((x, y, img.width, img.height))
    
    # 粘贴图片（带旋转和透明度）
    for i, (img, (x, y, w, h)) in enumerate(zip(processed_images, positions)):
        # 随机旋转角度（-15到15度）
        angle = random.uniform(-15, 15)
        rotated_img = img.rotate(angle, expand=False, fillcolor=(0, 0, 0, 0))
        
        # 调整透明度（模拟记忆碎片感）
        alpha = rotated_img.split()[3]
        alpha = alpha.point(lambda x: int(x * 0.85))  # 85%不透明度
        rotated_img.putalpha(alpha)
        
        # 粘贴到基图上
        base_img.paste(rotated_img, (x, y), rotated_img)
    
    # 加载字体 - 移动端优化尺寸
    font_title = None
    font_text = None
    font_size_title = int(base_width * 0.06)  # 响应式字体大小
    font_size_text = int(base_width * 0.04)
    
    # 字体路径列表，优先使用中文字体（支持云服务器环境）
    # 添加更多云服务器常用字体路径，确保能找到支持中文的字体
    font_paths = [
        # Linux 字体路径（云服务器常用，优先尝试）
        ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", None),  # 文泉驿微米黑
        ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", None),  # 文泉驿正黑
        ("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", None),  # Noto 中文字体
        ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", None),  # Noto 中文字体（OpenType）
        ("/usr/share/fonts/truetype/arphic/uming.ttc", None),  # AR PL UMing 中文字体
        ("/usr/share/fonts/truetype/arphic/ukai.ttc", None),  # AR PL UKai 中文字体
        ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", None),  # Droid Sans Fallback
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", None),  # Liberation Sans
        # Windows 字体路径
        ("C:/Windows/Fonts/msyh.ttc", None),  # 微软雅黑（优先，支持中文）
        ("C:/Windows/Fonts/msyhbd.ttc", None),  # 微软雅黑 Bold
        ("C:/Windows/Fonts/simhei.ttf", None),  # 黑体
        ("C:/Windows/Fonts/simsun.ttc", None),  # 宋体
        ("C:/Windows/Fonts/simkai.ttf", None),  # 楷体
        ("C:/Windows/Fonts/arial.ttf", None),  # Arial（英文，最后备选）
        # macOS 字体路径
        ("/System/Library/Fonts/PingFang.ttc", None),  # macOS 中文字体
        ("/System/Library/Fonts/STHeiti Light.ttc", None),  # macOS 黑体
        ("/System/Library/Fonts/Supplemental/PingFang.ttc", None),  # macOS PingFang 备选路径
        # 项目内字体（如果存在）
        ("assets/handwriting.ttf", None),  # 手写字体（如果支持中文）
        # 尝试使用系统默认字体目录
        (os.path.expanduser("~/Library/Fonts/PingFang.ttc"), None),  # macOS 用户字体目录
        (os.path.expanduser("~/.fonts/wqy-microhei.ttc"), None),  # Linux 用户字体目录
        (os.path.expanduser("~/.local/share/fonts/wqy-microhei.ttc"), None),  # Linux 用户字体目录（备选）
    ]
    
    # 尝试加载字体
    font_title = None
    font_text = None
    
    for path, index in font_paths:
        try:
            if os.path.exists(path):
                # 加载字体
                try:
                    # 对于 .ttc 文件，尝试不同的索引
                    if path.endswith('.ttc'):
                        # 尝试索引 0（通常包含常规字体）
                        try:
                            font_title = ImageFont.truetype(path, font_size_title, index=0)
                            font_text = ImageFont.truetype(path, font_size_text, index=0)
                        except:
                            # 如果索引 0 失败，尝试不指定索引
                            font_title = ImageFont.truetype(path, font_size_title)
                            font_text = ImageFont.truetype(path, font_size_text)
                    else:
                        font_title = ImageFont.truetype(path, font_size_title)
                        font_text = ImageFont.truetype(path, font_size_text)
                except Exception as e:
                    continue
                
                # 测试字体是否能正确渲染中文
                test_img = Image.new("RGB", (100, 100), "white")
                test_draw = ImageDraw.Draw(test_img)
                try:
                    # 测试中文字符
                    test_draw.text((0, 0), "年月日", font=font_title)
                    # 如果成功，使用这个字体
                    break
                except Exception as e:
                    # 如果测试失败，继续尝试下一个
                    font_title = None
                    font_text = None
                    continue
        except Exception as e:
            continue
    
    # 如果所有字体都加载失败，尝试使用PIL的默认字体
    # 如果默认字体也不可用，创建一个简单的字体对象用于渲染
    if font_title is None:
        try:
            # 尝试加载默认字体
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
        except:
            # 如果默认字体也失败，创建一个空字体对象（会在后续代码中处理）
            font_title = None
            font_text = None
    
    # 如果仍然没有字体，使用PIL的默认字体（可能不支持中文，但至少能显示）
    if font_title is None:
        try:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
        except:
            pass
    
    draw = ImageDraw.Draw(base_img)
    
    # 绘制日期和天气（左上角，略微旋转）
    # 增强颜色对比度，确保字体清晰可见
    date_weather_text = f"{date_str}  {weather}"
    
    # 计算文字宽度
    if font_title is not None:
        try:
            bbox = draw.textbbox((0, 0), date_weather_text, font=font_title)
            text_width = bbox[2] - bbox[0]
        except Exception as e:
            # 如果字体不支持某些字符，使用估算
            text_width = len(date_weather_text) * font_size_title * 0.6
    else:
        # 如果没有字体，使用估算（中文字符通常更宽）
        text_width = len(date_weather_text) * font_size_title * 0.8
    
    date_x = int(base_width * 0.08)
    date_y = int(base_height * 0.08)
    
    # 创建日期文字的临时图像以便旋转
    # 使用更深的颜色和更高的不透明度，确保字体清晰可见
    date_img = Image.new("RGBA", (int(text_width) + 100, font_size_title + 50), (0, 0, 0, 0))
    date_draw = ImageDraw.Draw(date_img)
    # 增强颜色对比度：使用更深的颜色 (60, 60, 80) 和更高的不透明度 (240)
    try:
        if font_title is not None:
            # 尝试使用字体绘制
            try:
                date_draw.text((50, 25), date_weather_text, fill=(60, 60, 80, 240), font=font_title)
            except Exception as e:
                # 如果字体不支持某些字符，尝试不使用字体
                date_draw.text((50, 25), date_weather_text, fill=(60, 60, 80, 240))
        else:
            # 如果没有字体，直接绘制（PIL会使用默认字体，可能不支持中文）
            # 如果默认字体不支持中文，至少显示日期数字部分
            try:
                date_draw.text((50, 25), date_weather_text, fill=(60, 60, 80, 240))
            except:
                # 如果还是失败，使用ASCII格式的日期
                ascii_date = date_str.replace("年", "-").replace("月", "-").replace("日", "")
                date_draw.text((50, 25), f"{ascii_date} {weather}", fill=(60, 60, 80, 240))
    except Exception as e:
        # 最后的降级方案：只显示日期数字
        try:
            ascii_date = date_str.replace("年", "-").replace("月", "-").replace("日", "")
            date_draw.text((50, 25), ascii_date, fill=(60, 60, 80, 240))
        except:
            pass
    
    date_img = date_img.rotate(-5, expand=False, fillcolor=(0, 0, 0, 0))
    base_img.paste(date_img, (date_x, date_y), date_img)
    
    # 绘制文字（非线性排版，模拟手写感）
    if text:
        lines = text.split('\n')
        # 文字起始位置（避开图片区域）- 移动端优化
        text_start_y = base_height // 2
        if processed_images:
            # 如果有多张图片，文字放在下方
            max_img_bottom = max([y + h for _, (x, y, w, h) in zip(processed_images, positions)])
            text_start_y = max_img_bottom + int(base_height * 0.1)
        
        current_y = text_start_y
        line_spacing = font_size_text * 1.5
        
        for i, line in enumerate(lines):
            if line.strip():
                # 每行略微不同的x位置（模拟手写）- 移动端优化
                x_offset = random.randint(-20, 20) if i > 0 else 0
                text_x = int(base_width * 0.1) + x_offset
                
                # 略微旋转（-3到3度）
                line_angle = random.uniform(-3, 3)
                
                # 创建单行文字的临时图像
                if font_text is not None:
                    try:
                        bbox = draw.textbbox((0, 0), line, font=font_text)
                        line_width = bbox[2] - bbox[0]
                        line_height = bbox[3] - bbox[1]
                    except:
                        line_width = len(line) * font_size_text * 0.6
                        line_height = font_size_text * 1.2
                else:
                    line_width = len(line) * font_size_text * 0.6
                    line_height = font_size_text * 1.2
                
                line_img = Image.new("RGBA", (int(line_width) + 100, int(line_height) + 50), (0, 0, 0, 0))
                line_draw = ImageDraw.Draw(line_img)
                # 增强颜色对比度：使用更深的颜色和更高的不透明度，确保字体清晰可见
                try:
                    if font_text is not None:
                        line_draw.text((50, 25), line, fill=(40, 40, 60, 250), font=font_text)
                    else:
                        # 如果没有字体，直接绘制（PIL会使用默认字体）
                        line_draw.text((50, 25), line, fill=(40, 40, 60, 250))
                except Exception as e:
                    # 如果绘制失败，尝试不使用字体
                    try:
                        line_draw.text((50, 25), line, fill=(40, 40, 60, 250))
                    except:
                        # 如果还是失败，跳过这一行
                        continue
                line_img = line_img.rotate(line_angle, expand=False, fillcolor=(0, 0, 0, 0))
                
                # 粘贴到基图
                base_img.paste(line_img, (int(text_x), int(current_y)), line_img)
                
                current_y += line_spacing + random.randint(-10, 10)  # 随机行间距变化
    
    # 如果有雾气层，最后叠加
    if os.path.exists(fog_path):
        try:
            fog = Image.open(fog_path).convert("RGBA")
            fog = fog.resize((base_width, base_height), Image.Resampling.LANCZOS)
            fog_alpha = fog.split()[3]
            fog_alpha = fog_alpha.point(lambda x: min(x, 80))  # 很低的透明度
            fog.putalpha(fog_alpha)
            base_img = Image.alpha_composite(base_img, fog)
        except:
            pass
    
    # 转换回RGB
    final_img = base_img.convert("RGB")
    
    return final_img

# ==========================================
# 5. CSS样式
# ==========================================
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    bg_base64 = get_base64_of_bin_file(bg_path) if os.path.exists(bg_path) else ""
except:
    bg_base64 = ""

st.markdown(
    f"""
    <style>
    
    /* 背景雨景图 - 透明度调整为0.4-0.5，兼顾氛围与内容可读性 */
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        position: relative;
    }}
    
    /* 背景层叠加，降低雨景图透明度（使用更轻的叠加层，避免黑屏） */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.25);
        z-index: 0 !important;
        pointer-events: none !important;
    }}
    
    /* 确保所有内容在背景层之上 */
    .main,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .block-container,
    div[data-testid="stVerticalBlock"] {{
        position: relative !important;
        z-index: 100 !important;
    }}
    
    /* 确保侧边栏在背景层之上，并且始终可见 */
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"] {{
        position: relative !important;
        z-index: 999 !important; /* 提高z-index确保在最上层 */
        visibility: visible !important;
        display: block !important;
        background-color: rgba(14, 17, 23, 0.95) !important; /* Streamlit默认侧边栏背景色 */
    }}
    
    /* 确保侧边栏内容可见 */
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div > div {{
        visibility: visible !important;
        display: block !important;
    }}
    
    /* 确保侧边栏按钮始终可见且可点击 */
    [data-testid="stSidebar"] [data-testid="baseButton-secondary"],
    [data-testid="stSidebar"] button {{
        visibility: visible !important;
        display: block !important;
        z-index: 1000 !important;
    }}
    header, footer, #MainMenu {{visibility: hidden;}}
    
    /* 确保侧边栏展开按钮始终可见 - 使用通用选择器，不依赖动态类名 */
    /* Streamlit侧边栏按钮的正确选择器 - 使用属性选择器更稳定 */
    [data-testid="stHeader"] > div:first-child button,
    [data-testid="stToolbar"] button,
    button[kind="header"],
    /* 通过位置选择器找到左上角的按钮 */
    header button,
    /* 确保所有header区域的按钮可见 */
    [data-testid="stHeader"] button {{
        visibility: visible !important;
        display: block !important;
        z-index: 9999 !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }}
    
    /* 确保侧边栏容器可见 */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"] {{
        visibility: visible !important;
        display: block !important;
        z-index: 999 !important; /* 提高z-index确保在最上层 */
        position: relative !important;
        background-color: rgba(14, 17, 23, 0.95) !important; /* Streamlit默认侧边栏背景色 */
    }}
    
    /* 确保侧边栏内容可见 */
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div > div {{
        visibility: visible !important;
        display: block !important;
    }}
    
    /* 确保header区域可见（包含侧边栏按钮） */
    [data-testid="stHeader"] {{
        visibility: visible !important;
        display: flex !important;
    }}
    
    /* 移动端响应式容器 */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    
    @media (max-width: 768px) {{
        .main .block-container {{
            padding: 1rem 0.5rem;
        }}
    }}
    
    /* 隐藏文件上传区域的所有文字提示和按钮 */
    .stFileUploader p,
    .stFileUploader span,
    .stFileUploader small,
    .stFileUploader button,
    .stFileUploader div[data-testid="stFileUploader"] p,
    .stFileUploader div[data-testid="stFileUploader"] span,
    .stFileUploader div[data-testid="stFileUploader"] small,
    .stFileUploader div[data-testid="stFileUploader"] button {{
        display: none !important;
        visibility: hidden !important;
    }}
    
    /* ============================================
       核心颜色规则：雨窗背景层的文字样式
       ============================================ */
    /* 标题、页面提示、说明文字等 - 浅色（淡米色#F5F5F5）+ 1px轻微黑色文字阴影 */
    h1, h2, h3, h4, h5, h6 {{
        color: #F5F5F5 !important;
        text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2) !important;
    }}
    
    /* 普通文本、标签、说明文字 */
    p, label, span, div {{
        color: #F5F5F5 !important;
        text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2) !important;
    }}
    
    /* 输入框、下拉框、文本区域的标签 */
    .stDateInput label,
    .stSelectbox label,
    .stTextInput label,
    .stTextArea label,
    .stFileUploader label {{
        color: #F5F5F5 !important;
        font-weight: 500 !important;
        text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2) !important;
    }}
    
    /* ============================================
       输入框、下拉框、文本区域等组件样式
       ============================================ */
    /* 统一磨砂玻璃质感：8px圆角 + 轻微阴影 */
    .stDateInput > div > div,
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stFileUploader > div {{
        background-color: rgba(45, 45, 45, 0.5) !important; /* #2D2D2D80 */
        border-radius: 8px !important;
        border: 1px solid rgba(224, 224, 224, 0.5) !important; /* #E0E0E0 半透明 */
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.125) !important; /* #00000020 */
        transition: all 0.3s ease !important;
    }}
    
    /* 组件内文字颜色：纯白色 */
    .stDateInput input,
    .stSelectbox select,
    .stTextInput input,
    .stTextArea textarea {{
        color: #FFFFFF !important;
        background-color: transparent !important;
    }}
    
    /* 占位符颜色 */
    input::placeholder,
    textarea::placeholder {{
        color: rgba(255, 255, 255, 0.6) !important;
    }}
    
    /* 选中状态：边框淡蓝色#6699cc（半透明），背景色轻微提亮 */
    .stDateInput > div > div:focus-within,
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {{
        border-color: rgba(102, 153, 204, 0.7) !important; /* #6699cc 半透明 */
        background-color: rgba(51, 51, 51, 0.6) !important; /* #33333390 轻微提亮 */
        outline: none !important;
    }}
    
    /* 天气选择下拉框 - 图标与文字对齐，确保文字完整显示 */
    .stSelectbox select {{
        padding-left: 8px !important;
        padding-right: 30px !important; /* 为下拉箭头留出空间 */
        line-height: 1.5 !important;
        min-width: 120px !important; /* 确保有足够宽度显示完整文字 */
        width: 100% !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }}
    
    /* 确保下拉框容器有足够宽度 */
    .stSelectbox > div > div {{
        min-width: 120px !important;
        width: 100% !important;
    }}
    
    /* ============================================
       今日随笔输入框特殊样式
       ============================================ */
    .stTextArea textarea {{
        background-color: rgba(45, 45, 45, 0.5) !important; /* #2D2D2D80 */
        color: #FFFFFF !important;
        font-size: 18px;
        border-radius: 8px !important;
        border: 1px solid rgba(224, 224, 224, 0.5) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.125) !important;
        transition: all 0.3s ease !important;
    }}
    
    .stTextArea textarea:focus {{
        border-color: rgba(102, 153, 204, 0.7) !important;
        background-color: rgba(51, 51, 51, 0.6) !important;
        color: #FFFFFF !important;
        outline: none !important;
    }}
    
    /* ============================================
       文件上传区域样式 - 优化视觉效果
       ============================================ */
    .stFileUploader > div {{
        background-color: rgba(45, 45, 45, 0.5) !important; /* #2D2D2D80 */
        border-radius: 8px !important;
        border: 2px dashed rgba(224, 224, 224, 0.4) !important; /* 虚线边框，更优雅 */
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.125) !important;
        min-height: 120px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        transition: all 0.3s ease !important;
    }}
    
    /* 悬停效果 */
    .stFileUploader > div:hover {{
        border-color: rgba(224, 224, 224, 0.6) !important;
        background-color: rgba(45, 45, 45, 0.6) !important;
    }}
    
    /* 极简风格：只显示"＋"号图标 */
    .stFileUploader > div::after {{
        content: "+" !important;
        font-size: 48px !important;
        color: rgba(245, 245, 245, 0.7) !important; /* #F5F5F5 半透明 */
        font-weight: 300 !important;
        line-height: 1 !important;
        display: block !important;
        text-align: center !important;
        position: absolute !important;
        pointer-events: none !important;
        z-index: 1 !important;
    }}
    
    /* ============================================
       按钮组件样式
       ============================================ */
    .stButton button {{
        background-color: rgba(45, 45, 45, 0.56) !important; /* #2D2D2D90 */
        color: #FFFFFF !important;
        border: 1px solid rgba(224, 224, 224, 0.5) !important;
        border-radius: 8px !important;
        padding: 8px 24px;
        white-space: nowrap !important;
        width: auto !important;
        min-height: 44px;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.125) !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton button:hover {{
        background-color: rgba(26, 26, 26, 0.56) !important; /* #1A1A1A90 */
        transform: scale(1.02) !important;
        border-color: rgba(224, 224, 224, 0.7) !important;
    }}
    
    /* ============================================
       移动端优化
       ============================================ */
    @media (max-width: 768px) {{
        /* 移动端组件上下间距≥15px，宽度占屏幕85% */
        .main .block-container {{
            padding: 1rem 0.5rem;
            max-width: 85% !important;
            margin: 0 auto !important;
        }}
        
        /* 组件间距 */
        .stDateInput,
        .stSelectbox,
        .stTextArea,
        .stFileUploader,
        .stButton {{
            margin-top: 15px !important;
            margin-bottom: 15px !important;
        }}
        
        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {{
            color: #F5F5F5 !important;
            text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2) !important;
            font-size: 1.2rem !important;
            margin-top: 0.5rem !important;
        }}
        
        /* 文本区域移动端优化 */
        .stTextArea textarea {{
            font-size: 16px;
            padding: 12px !important;
        }}
        
        /* 文件上传区域移动端优化 */
        .stFileUploader > div {{
            padding: 1rem !important;
            min-height: 100px !important;
        }}
        
        .stFileUploader > div::after {{
            font-size: 40px !important;
        }}
        
        /* 按钮移动端优化 */
        .stButton button {{
            padding: 12px 28px;
            font-size: 16px;
            width: 100% !important;
        }}
        
        /* 日期和天气输入框移动端优化 */
        .stDateInput > div > div,
        .stSelectbox > div > div {{
            font-size: 14px !important;
            padding: 8px !important;
            min-height: 44px !important;
        }}
        
        .stDateInput label,
        .stSelectbox label {{
            font-size: 13px !important;
            margin-bottom: 4px !important;
        }}
        
        /* 确保日期和天气在移动端也保持一行显示 */
        div[data-testid="column"] {{
            min-width: 0 !important;
            flex: 1 1 0% !important;
        }}
    }}
    
    
    /* ============================================
       手账卡片样式
       ============================================ */
    .journal-card {{
        background-color: rgba(45, 45, 45, 0.5) !important; /* #2D2D2D80 */
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border-radius: 8px !important;
        padding: 20px;
        margin: 15px 0 !important;
        border: 1px solid rgba(224, 224, 224, 0.5) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.125) !important;
    }}
    
    @media (max-width: 768px) {{
        .journal-card {{
            padding: 15px;
            margin: 15px 0 !important;
            width: 85% !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}
    }}
    
    /* ============================================
       列表视图（expander）样式优化
       ============================================ */
    .streamlit-expanderHeader {{
        background-color: rgba(45, 45, 45, 0.5) !important; /* #2D2D2D80 */
        color: #F5F5F5 !important;
        border: 1px solid rgba(224, 224, 224, 0.5) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin-bottom: 8px !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.125) !important;
        text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }}
    
    .streamlit-expanderHeader:hover {{
        background-color: rgba(51, 51, 51, 0.6) !important; /* #33333390 */
        border-color: rgba(224, 224, 224, 0.7) !important;
    }}
    
    .streamlit-expanderContent {{
        background-color: rgba(45, 45, 45, 0.4) !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin-top: 8px !important;
        border: 1px solid rgba(224, 224, 224, 0.3) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.125) !important;
    }}
    
    /* 列表视图中的文字颜色 */
    .streamlit-expanderContent p,
    .streamlit-expanderContent div,
    .streamlit-expanderContent label,
    .streamlit-expanderContent strong {{
        color: #F5F5F5 !important;
        text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2) !important;
    }}
    
    /* 列表视图中的按钮样式 */
    .streamlit-expanderContent button {{
        color: #FFFFFF !important;
        background-color: rgba(45, 45, 45, 0.56) !important;
        border: 1px solid rgba(224, 224, 224, 0.5) !important;
        border-radius: 8px !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.125) !important;
        transition: all 0.3s ease !important;
    }}
    
    .streamlit-expanderContent button:hover {{
        background-color: rgba(26, 26, 26, 0.56) !important;
        transform: scale(1.02) !important;
    }}
    
    @media (max-width: 768px) {{
        .streamlit-expanderHeader {{
            font-size: 14px !important;
            padding: 10px !important;
            margin-bottom: 15px !important;
        }}
        
        .streamlit-expanderContent {{
            padding: 12px !important;
            margin-top: 15px !important;
        }}
    }}
    
    /* 图片响应式 */
    .stImage img {{
        border-radius: 12px;
    }}
    
    @media (max-width: 768px) {{
        .stImage img {{
            max-width: 100%;
            height: auto;
        }}
    }}
    
    /* 标题优化 */
    h3 {{
        font-size: 1.5rem;
    }}
    
    @media (max-width: 768px) {{
        h3 {{
            font-size: 1.2rem;
            margin-top: 0.5rem;
        }}
    }}
    
    /* 侧边栏移动端优化 - 移除动态类名，使用通用选择器 */
    @media (max-width: 768px) {{
        [data-testid="stSidebar"] {{
            padding-top: 1rem;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 6. 主应用逻辑
# ==========================================
# 侧边栏导航 - 移动端优化
st.sidebar.title("📖 MoodJournal")

# 添加一个提示，帮助用户知道如何打开侧边栏
st.sidebar.markdown("---")
st.sidebar.markdown("💡 **提示：** 如果侧边栏被隐藏，点击页面左上角的 `>` 按钮可以展开")

page = st.sidebar.radio(
    "导航",
    ["✨ 新建日记", "⚙️ 管理手账"],
    label_visibility="collapsed"
)

if page == "✨ 新建日记":
    st.markdown("<div style='height: 3vh;'></div>", unsafe_allow_html=True)
    
    st.markdown("### 🌸 记录今天的美好瞬间")
    
    # 日期和天气选择 - 一行显示（移动端也保持一行）
    # 使用更紧凑的列布局，确保移动端也在一行
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        selected_date = st.date_input("📅 日期", value=date.today())
    with col2:
        weather_options = ["☀️ 晴天", "⛅ 多云", "🌧️ 雨天", "❄️ 雪天", "🌫️ 雾天", "🌙 夜晚"]
        selected_weather = st.selectbox("🌤️ 天气", weather_options)
    
    # 图片上传
    st.markdown("### 📸 美好瞬间")
    uploaded_files = st.file_uploader(
        "",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        help="最多上传3张图片",
        label_visibility="collapsed"
    )
    
    if len(uploaded_files) > 3:
        st.warning("⚠️ 最多只能上传3张图片，已自动选择前3张")
        uploaded_files = uploaded_files[:3]
    
    # 显示预览 - 移动端优化，限制预览大小
    if uploaded_files:
        num_cols = min(len(uploaded_files), 3)
        cols = st.columns(num_cols)
        for i, uploaded_file in enumerate(uploaded_files[:3]):
            with cols[i]:
                # 限制预览图宽度，移动端更小（150px）
                st.image(uploaded_file, width=150)
    
    # 文字输入 - 移动端优化高度
    st.markdown("### ✍️ 今日随笔")
    journal_text = st.text_area(
        "写下你的心情...",
        height=150,
        placeholder="让思绪在雾气中流淌...",
        label_visibility="collapsed"
    )
    
    # 生成按钮 - 移动端优化布局
    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        generate_btn = st.button("✨ 制作手账", use_container_width=True)
    
    # 生成逻辑
    if generate_btn:
        if not journal_text and not uploaded_files:
            st.warning("请至少上传一张图片或输入一些文字")
        else:
            with st.spinner("🌧️ 正在生成你的情绪手帐..."):
                try:
                    # 保存图片
                    saved_image_paths = []
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            img_path = save_image(uploaded_file)
                            saved_image_paths.append(img_path)
                    
                    # 生成手帐
                    date_str = selected_date.strftime("%Y年%m月%d日")
                    journal_image = create_journal_page(
                        saved_image_paths,
                        journal_text,
                        date_str,
                        selected_weather
                    )
                    
                    # 保存生成的手帐图片
                    journal_id = str(uuid.uuid4())
                    journal_filename = f"journal_{journal_id}.png"
                    
                    # 上传到Supabase Storage或保存到本地
                    if SUPABASE_AVAILABLE:
                        try:
                            journal_image_url = upload_image_to_supabase(
                                journal_image, 
                                journal_filename, 
                                folder="journals"
                            )
                            if journal_image_url:
                                journal_image_path = journal_image_url
                            else:
                                # 降级到本地
                                journal_image_path = os.path.join(IMAGES_DIR, journal_filename)
                                journal_image.save(journal_image_path, "PNG")
                        except Exception as e:
                            st.warning(f"⚠️ Supabase上传失败，使用本地存储：{str(e)}")
                            journal_image_path = os.path.join(IMAGES_DIR, journal_filename)
                            journal_image.save(journal_image_path, "PNG")
                    else:
                        # 本地存储
                        journal_image_path = os.path.join(IMAGES_DIR, journal_filename)
                        journal_image.save(journal_image_path, "PNG")
                    
                    # 保存日记条目
                    journal_entry = {
                        "id": journal_id,
                        "date": date_str,
                        "weather": selected_weather,
                        "text": journal_text,
                        "image_paths": saved_image_paths,
                        "journal_image_path": journal_image_path,
                        "created_at": datetime.now().isoformat()
                    }
                    save_journal(journal_entry)
                    
                    # 显示结果
                    st.success("✨ 手帐生成成功！")
                    st.markdown("### 📖 你的手帐")
                    # 限制预览图大小，移动端更友好
                    st.image(journal_image, width=600)
                    
                    # 下载按钮
                    buf = BytesIO()
                    journal_image.save(buf, format="PNG")
                    buf.seek(0)
                    st.download_button(
                        label="📥 下载手帐",
                        data=buf,
                        file_name=f"journal_{date_str}.png",
                        mime="image/png"
                    )
                    
                    # 清空输入（通过重新运行）
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"生成失败：{str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

elif page == "⚙️ 管理手账":
    st.markdown("<div style='height: 2vh;'></div>", unsafe_allow_html=True)
    st.markdown("### ⚙️ 管理手账")
    
    journals = load_journals()
    
    if not journals:
        st.info("还没有任何记录，去创建第一篇日记吧！")
    else:
        # 按日期倒序排列
        journals.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # 视图切换
        view_mode = st.radio(
            "📖 视图模式",
            ["📋 列表视图", "📚 手账本视图"],
            horizontal=True,
            key="view_mode"
        )
        
        # 搜索和筛选功能
        col1, col2 = st.columns([2, 1])
        with col1:
            search_keyword = st.text_input("🔍 搜索", placeholder="输入日期、天气或文字内容...", key="search_input")
        with col2:
            weather_filter = st.selectbox("🌤️ 筛选天气", ["全部", "☀️ 晴天", "⛅ 多云", "🌧️ 雨天", "❄️ 雪天", "🌫️ 雾天", "🌙 夜晚"])
        
        # 筛选手账（优先使用Supabase，降级到本地搜索）
        if SUPABASE_AVAILABLE:
            try:
                if search_keyword:
                    filtered_journals = search_journals_in_supabase(search_keyword)
                else:
                    filtered_journals = load_journals_from_supabase()
                
                if weather_filter != "全部":
                    filtered_journals = filter_journals_by_weather(weather_filter)
                
                # 转换格式以兼容现有代码
                for journal in filtered_journals:
                    if "journal_image_url" in journal:
                        journal["journal_image_path"] = journal["journal_image_url"]
            except Exception as e:
                st.warning(f"⚠️ Supabase搜索失败，使用本地搜索：{str(e)}")
                # 降级到本地搜索
                filtered_journals = journals
                if search_keyword:
                    filtered_journals = [
                        j for j in filtered_journals
                        if search_keyword in j.get("date", "") 
                        or search_keyword in j.get("weather", "")
                        or search_keyword in j.get("text", "")
                    ]
                if weather_filter != "全部":
                    filtered_journals = [j for j in filtered_journals if j.get("weather", "") == weather_filter]
        else:
            # 本地搜索
            filtered_journals = journals
            if search_keyword:
                filtered_journals = [
                    j for j in filtered_journals
                    if search_keyword in j.get("date", "") 
                    or search_keyword in j.get("weather", "")
                    or search_keyword in j.get("text", "")
                ]
            if weather_filter != "全部":
                filtered_journals = [j for j in filtered_journals if j.get("weather", "") == weather_filter]
        
        if view_mode == "📚 手账本视图":
            # 手账本翻页视图（仅查看）
            st.markdown("---")
            
            # 初始化页码（使用筛选后的列表作为key的一部分，确保筛选变化时重置）
            if filtered_journals:
                first_id = str(filtered_journals[0].get('id', ''))
            else:
                first_id = ''
            filter_key = f"filtered_{len(filtered_journals)}_{hash(first_id)}"
            page_key = f"current_page_{filter_key}"
            
            if page_key not in st.session_state:
                st.session_state[page_key] = 0
            
            total_pages = len(filtered_journals)
            
            if total_pages == 0:
                st.info("没有找到匹配的记录")
            else:
                current_page = st.session_state[page_key]
                
                # 确保页码在有效范围内
                if current_page >= total_pages:
                    current_page = total_pages - 1
                    st.session_state[page_key] = current_page
                if current_page < 0:
                    current_page = 0
                    st.session_state[page_key] = current_page
                
                # 重新读取当前页码（确保使用最新值）
                current_page = st.session_state[page_key]
                current_journal = filtered_journals[current_page]
                
                st.markdown("---")
                
                # 手账本页面样式（优化版：更优雅的视觉效果）
                st.markdown("""
                <style>
                /* 手账图片容器 - 添加优雅的阴影和边框 */
                .journal-image-wrapper {
                    display: inline-block;
                    padding: 15px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    box-shadow: 
                        0 8px 32px rgba(0, 0, 0, 0.3),
                        0 2px 8px rgba(0, 0, 0, 0.2),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    -webkit-backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    transition: all 0.3s ease;
                    animation: pageFlip 0.6s ease-in-out;
                }
                .journal-image-wrapper:hover {
                    transform: translateY(-2px);
                    box-shadow: 
                        0 12px 40px rgba(0, 0, 0, 0.4),
                        0 4px 12px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.15);
                }
                .journal-image-wrapper img {
                    border-radius: 8px;
                    display: block;
                }
                
                /* 翻页动画 */
                @keyframes pageFlip {
                    0% {
                        opacity: 0;
                        transform: perspective(1000px) rotateY(-10deg) scale(0.95);
                    }
                    50% {
                        transform: perspective(1000px) rotateY(5deg) scale(0.98);
                    }
                    100% {
                        opacity: 1;
                        transform: perspective(1000px) rotateY(0deg) scale(1);
                    }
                }
                
                /* 翻页按钮优化 - 更美观的圆形按钮 */
                .nav-button-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 400px;
                }
                /* 翻页按钮样式 */
                .nav-button-container button {
                    width: 50px !important;
                    height: 50px !important;
                    border-radius: 50% !important;
                    background: rgba(255, 255, 255, 0.15) !important;
                    backdrop-filter: blur(10px) !important;
                    -webkit-backdrop-filter: blur(10px) !important;
                    border: 1px solid rgba(255, 255, 255, 0.3) !important;
                    color: rgba(255, 255, 255, 0.9) !important;
                    font-size: 20px !important;
                    font-weight: 300 !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    transition: all 0.3s ease !important;
                    cursor: pointer !important;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
                }
                .nav-button-container button:hover:not(:disabled) {
                    background: rgba(255, 255, 255, 0.25) !important;
                    transform: scale(1.1) !important;
                    box-shadow: 0 4px 12px rgba(255, 255, 255, 0.3) !important;
                    border-color: rgba(255, 255, 255, 0.5) !important;
                }
                .nav-button-container button:active:not(:disabled) {
                    transform: scale(0.95) !important;
                }
                .nav-button-container button:disabled {
                    opacity: 0.3 !important;
                    cursor: not-allowed !important;
                }
                
                /* 页码信息优化 - 更优雅的卡片样式 */
                .page-info-card {
                    display: inline-block;
                    padding: 12px 20px;
                    background: rgba(255, 255, 255, 0.08);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    color: rgba(255, 255, 255, 0.95);
                    font-size: 14px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }
                .page-info-card .main-text {
                    font-weight: 500;
                    letter-spacing: 0.5px;
                }
                .page-info-card .sub-text {
                    font-size: 11px;
                    color: rgba(255, 255, 255, 0.7);
                    margin-top: 4px;
                    font-weight: 300;
                }
                
                /* 跳转输入框优化 */
                .jump-input-wrapper {
                    display: inline-block;
                    margin-left: 12px;
                }
                .jump-input-wrapper div[data-testid="stTextInput"] > div > div > input {
                    width: 45px !important;
                    padding: 6px 8px !important;
                    font-size: 13px !important;
                    text-align: center;
                    height: 28px !important;
                    background: rgba(255, 255, 255, 0.1) !important;
                    border: 1px solid rgba(255, 255, 255, 0.2) !important;
                    border-radius: 8px !important;
                    color: white !important;
                    backdrop-filter: blur(10px);
                }
                .jump-input-wrapper div[data-testid="stTextInput"] > div > div > input:focus {
                    background: rgba(255, 255, 255, 0.15) !important;
                    border-color: rgba(255, 255, 255, 0.4) !important;
                    box-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
                }
                .jump-input-wrapper div[data-testid="stTextInput"] > div > div > input::placeholder {
                    color: rgba(255, 255, 255, 0.5) !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # 显示当前页的手账（仅显示生成的手账图片，居中，翻页按钮在左右两侧）
                # 调整列比例（左右按钮列更窄，中间图片列更宽，确保视觉居中）
                col_left_btn, col_center_img, col_right_btn = st.columns([1, 6, 1])
                
                journal_img_path = current_journal.get("journal_image_path")
                img_height = 500  # 保持按钮垂直居中的基准高度
                
                with col_left_btn:
                    # 左箭头按钮（垂直居中，优化样式）
                    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
                    prev_clicked = st.button("◀", disabled=(current_page == 0), use_container_width=False, key="prev_btn_side", help="上一页")
                    if prev_clicked:
                        if current_page > 0:
                            st.session_state[page_key] = current_page - 1
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_center_img:
                    # 图片容器（添加优雅的包装）
                    journal_img_path = current_journal.get("journal_image_path") or current_journal.get("journal_image_url")
                    if journal_img_path:
                        # 支持URL和本地路径
                        if journal_img_path.startswith(('http://', 'https://')) or os.path.exists(journal_img_path):
                            st.markdown('<div class="journal-image-wrapper">', unsafe_allow_html=True)
                            st.image(journal_img_path, width=380)
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.info("手账图片未找到")
                    else:
                        st.info("手账图片未找到")
                
                with col_right_btn:
                    # 右箭头按钮（垂直居中，优化样式）
                    st.markdown('<div class="nav-button-container">', unsafe_allow_html=True)
                    next_clicked = st.button("▶", disabled=(current_page == total_pages - 1), use_container_width=False, key="next_btn_side", help="下一页")
                    if next_clicked:
                        if current_page < total_pages - 1:
                            st.session_state[page_key] = current_page + 1
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # 翻页控制（放在手账本下方，跳转输入框和页码信息相邻）
                st.markdown("---")
                
                # 初始化跳转输入框的值
                jump_input_key = f"jump_input_{page_key}"
                if jump_input_key not in st.session_state:
                    st.session_state[jump_input_key] = str(current_page + 1)
                elif int(st.session_state.get(jump_input_key, str(current_page + 1))) != current_page + 1:
                    st.session_state[jump_input_key] = str(current_page + 1)
                
                def on_jump_change():
                    try:
                        jump_value = int(st.session_state[jump_input_key])
                        if 1 <= jump_value <= total_pages:
                            new_page = jump_value - 1
                            if new_page != current_page:
                                st.session_state[page_key] = new_page
                                st.rerun()
                    except ValueError:
                        st.session_state[jump_input_key] = str(current_page + 1)
                
                # 页码控制和跳转（优化布局）
                st.markdown("---")
                st.markdown('<div style="text-align: center; padding: 15px 0;">', unsafe_allow_html=True)
                
                # 使用列布局让它们在同一行
                col_info, col_jump = st.columns([2.5, 0.5])
                
                with col_info:
                    # 页码和时间显示（优雅的卡片样式）
                    st.markdown(f"""
                    <div class="page-info-card">
                        <div class="main-text">
                            📖 第 <strong>{current_page + 1}</strong> 页 / 共 <strong>{total_pages}</strong> 页
                        </div>
                        <div class="sub-text">
                            {current_journal.get('date', '未知日期')} {current_journal.get('weather', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_jump:
                    # 输入框（优化样式，放在页码信息右边）
                    st.markdown("<div class='jump-input-wrapper'>", unsafe_allow_html=True)
                    st.text_input(
                        "",
                        value=st.session_state[jump_input_key],
                        key=jump_input_key,
                        label_visibility="collapsed",
                        on_change=on_jump_change,
                        help="输入页码后按回车跳转"
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        else:
            # 列表视图（原有功能）
            st.markdown(f"**共找到 {len(filtered_journals)} 条记录**")
            st.markdown("---")
            
            # 显示手账列表
            for idx, journal in enumerate(filtered_journals):
                journal_id = journal.get("id", "")
                date_str = journal.get("date", "未知日期")
                weather = journal.get("weather", "")
                text = journal.get("text", "")
                
                with st.expander(f"📅 {date_str} {weather}", expanded=False):
                    # 操作按钮
                    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                    
                    with col_btn1:
                        if st.button("👁️ 查看", key=f"view_{journal_id}"):
                            st.session_state[f"view_journal_{journal_id}"] = True
                    
                    with col_btn2:
                        if st.button("✏️ 编辑", key=f"edit_{journal_id}"):
                            st.session_state[f"edit_journal_{journal_id}"] = True
                    
                    with col_btn3:
                        if st.button("🗑️ 删除", key=f"delete_{journal_id}"):
                            st.session_state[f"delete_journal_{journal_id}"] = True
                    
                    with col_btn4:
                        journal_img_path = journal.get("journal_image_path") or journal.get("journal_image_url")
                        if journal_img_path:
                            # 支持URL和本地路径
                            if journal_img_path.startswith(('http://', 'https://')) or os.path.exists(journal_img_path):
                                buf = BytesIO()
                                img = load_image_from_path_or_url(journal_img_path)
                                if img:
                                    img.save(buf, format="PNG")
                                    buf.seek(0)
                                    st.download_button(
                                        "📥 下载",
                                        data=buf,
                                        file_name=f"journal_{date_str}.png",
                                        mime="image/png",
                                        key=f"download_{journal_id}"
                                    )
                    
                    # 显示详情
                    if st.session_state.get(f"view_journal_{journal_id}", False):
                        st.markdown("#### 📖 手账详情")
                        journal_img_path = journal.get("journal_image_path") or journal.get("journal_image_url")
                        if journal_img_path:
                            # 支持URL和本地路径
                            if journal_img_path.startswith(('http://', 'https://')):
                                st.image(journal_img_path, width=600)
                            elif os.path.exists(journal_img_path):
                                st.image(journal_img_path, width=600)
                        
                        if text:
                            st.markdown(f"**随笔：** {text}")
                        
                        original_images = journal.get("image_paths", [])
                        if original_images:
                            st.markdown("**原始图片：**")
                            num_cols = min(len(original_images), 3)
                            cols = st.columns(num_cols)
                            for i, img_path in enumerate(original_images[:3]):
                                # 支持URL和本地路径
                                if img_path.startswith(('http://', 'https://')) or os.path.exists(img_path):
                                    with cols[i]:
                                        st.image(img_path, width=150)
                    
                    # 编辑功能
                    if st.session_state.get(f"edit_journal_{journal_id}", False):
                        st.markdown("#### ✏️ 编辑手账")
                        
                        # 加载原始数据
                        try:
                            # 解析日期字符串（格式：2025年12月04日）
                            date_parts = date_str.replace("年", "-").replace("月", "-").replace("日", "").split("-")
                            if len(date_parts) == 3:
                                edit_date_value = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
                            else:
                                edit_date_value = date.today()
                        except:
                            edit_date_value = date.today()
                        
                        edit_date = st.date_input("📅 日期", value=edit_date_value, key=f"edit_date_{journal_id}")
                        weather_options = ["☀️ 晴天", "⛅ 多云", "🌧️ 雨天", "❄️ 雪天", "🌫️ 雾天", "🌙 夜晚"]
                        current_weather_idx = weather_options.index(weather) if weather in weather_options else 0
                        edit_weather = st.selectbox("🌤️ 天气", weather_options, index=current_weather_idx, key=f"edit_weather_{journal_id}")
                        edit_text = st.text_area("✍️ 今日随笔", value=text, height=150, key=f"edit_text_{journal_id}")
                        
                        # 显示原始图片（暂时不支持重新上传）
                        original_images = journal.get("image_paths", [])
                        if original_images:
                            st.markdown("**原始图片（暂不支持修改）：**")
                            num_cols = min(len(original_images), 3)
                            cols = st.columns(num_cols)
                            for i, img_path in enumerate(original_images[:3]):
                                # 支持URL和本地路径
                                if img_path.startswith(('http://', 'https://')) or os.path.exists(img_path):
                                    with cols[i]:
                                        st.image(img_path, width=150)
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 保存并重新生成", key=f"save_{journal_id}"):
                                with st.spinner("🌧️ 正在重新生成手账..."):
                                    try:
                                        # 重新生成手账
                                        edit_date_str = edit_date.strftime("%Y年%m月%d日")
                                        new_journal_image = create_journal_page(
                                            original_images,
                                            edit_text,
                                            edit_date_str,
                                            edit_weather
                                        )
                                        
                                        # 保存新的手账图片
                                        journal_filename = f"journal_{journal_id}.png"
                                        
                                        if SUPABASE_AVAILABLE:
                                            try:
                                                # 上传到Supabase Storage（覆盖）
                                                new_journal_image_url = upload_image_to_supabase(
                                                    new_journal_image,
                                                    journal_filename,
                                                    folder="journals"
                                                )
                                                if new_journal_image_url:
                                                    journal["journal_image_path"] = new_journal_image_url
                                                    journal["journal_image_url"] = new_journal_image_url
                                            except Exception as e:
                                                st.warning(f"⚠️ Supabase上传失败，使用本地存储：{str(e)}")
                                                journal_image_path = os.path.join(IMAGES_DIR, journal_filename)
                                                new_journal_image.save(journal_image_path, "PNG")
                                                journal["journal_image_path"] = journal_image_path
                                        else:
                                            # 本地存储
                                            journal_image_path = os.path.join(IMAGES_DIR, journal_filename)
                                            new_journal_image.save(journal_image_path, "PNG")
                                            journal["journal_image_path"] = journal_image_path
                                        
                                        # 更新日记条目
                                        update_data = {
                                            "date": edit_date_str,
                                            "weather": edit_weather,
                                            "text": edit_text,
                                            "journal_image_url": journal.get("journal_image_path") or journal.get("journal_image_url")
                                        }
                                        
                                        if SUPABASE_AVAILABLE:
                                            # 使用Supabase更新
                                            if update_journal_in_supabase(journal_id, update_data):
                                                st.success("✨ 手账已更新！")
                                                st.session_state[f"edit_journal_{journal_id}"] = False
                                                st.rerun()
                                            else:
                                                st.error("更新失败：Supabase更新失败")
                                        else:
                                            # 本地文件更新
                                            journal["date"] = edit_date_str
                                            journal["weather"] = edit_weather
                                            journal["text"] = edit_text
                                            journal["created_at"] = datetime.now().isoformat()
                                            
                                            all_journals = load_journals()
                                            for i, j in enumerate(all_journals):
                                                if j.get("id") == journal_id:
                                                    all_journals[i] = journal
                                                    break
                                            save_journals(all_journals)
                                            st.success("✨ 手账已更新！")
                                            st.session_state[f"edit_journal_{journal_id}"] = False
                                            st.rerun()
                                        
                                    except Exception as e:
                                        st.error(f"更新失败：{str(e)}")
                        
                        with col_cancel:
                            if st.button("❌ 取消", key=f"cancel_{journal_id}"):
                                st.session_state[f"edit_journal_{journal_id}"] = False
                                st.rerun()
                    
                    # 删除功能
                    if st.session_state.get(f"delete_journal_{journal_id}", False):
                        st.warning(f"⚠️ 确定要删除 {date_str} 的手账吗？此操作不可恢复！")
                        col_del, col_cancel_del = st.columns(2)
                        with col_del:
                            if st.button("🗑️ 确认删除", key=f"confirm_delete_{journal_id}", type="primary"):
                                try:
                                    if SUPABASE_AVAILABLE:
                                        # 使用Supabase删除
                                        if delete_journal_from_supabase(journal_id):
                                            st.success("🗑️ 手账已删除")
                                            st.session_state[f"delete_journal_{journal_id}"] = False
                                            st.rerun()
                                        else:
                                            st.error("删除失败：Supabase删除失败")
                                    else:
                                        # 本地文件删除
                                        journal_img_path = journal.get("journal_image_path")
                                        if journal_img_path and os.path.exists(journal_img_path):
                                            os.remove(journal_img_path)
                                        
                                        # 删除原始图片文件
                                        for img_path in journal.get("image_paths", []):
                                            if os.path.exists(img_path):
                                                os.remove(img_path)
                                        
                                        # 从列表中删除
                                        all_journals = load_journals()
                                        all_journals = [j for j in all_journals if j.get("id") != journal_id]
                                        save_journals(all_journals)
                                        
                                        st.success("🗑️ 手账已删除")
                                        st.session_state[f"delete_journal_{journal_id}"] = False
                                        st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"删除失败：{str(e)}")
                        
                        with col_cancel_del:
                            if st.button("❌ 取消", key=f"cancel_delete_{journal_id}"):
                                st.session_state[f"delete_journal_{journal_id}"] = False
                                st.rerun()
                    
                    st.markdown("---")
