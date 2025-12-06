import streamlit as st
from openai import OpenAI
import os

# === 1. 基础配置 ===
# 请确保这里填的是你的 OneAPI 地址 (末尾带 /v1) 和 令牌
API_BASE = os.getenv("API_BASE", "https://api.your-oneapi-domain.com/v1") 
API_KEY = os.getenv("API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxx")

# === 模型映射配置 ===
TEXT_MODELS_MAP = {
    "DeepSeek V3.2": "deepseek-ai/DeepSeek-V3.2-Exp",
    "Qwen3 14B": "Qwen/Qwen3-14B",
    "Gemini 2.5": "gemini-2.5-flash",
    "Qwen Coder 480B": "Qwen/Qwen3-coder-480b-a35b-instruct" 
}

IMAGE_MODELS_MAP = {
    "Kwai Kolors": "Kwai-Kolors/Kolors",
    "Qwen Image": "Qwen/Qwen-Image",
    # --- 通义万相 Turbo 模型 ---
    "Tongyi Turbo": "Tongyi-MAI/Z-Image-Turbo"
}

# === 新增：分辨率与比例映射配置 ===
# 这里定义了不同比例下，OneAPI/常用模型通常支持的标准分辨率
ASPECT_RATIOS = {
    "1:1 (方形构图)": ["1024x1024", "512x512", "2048x2048"],
    "3:4 (小红书/海报)": ["768x1024", "1152x1536"],
    "4:3 (标准屏幕)": ["1024x768", "1536x1152"],
    "9:16 (手机竖屏)": ["720x1280", "1024x1792"],
    "16:9 (电影宽屏)": ["1280x720", "1792x1024"]
}

# === 2. 页面设置 ===
st.set_page_config(
    page_title="未湃 WAPI · AI 智能工作台",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === 3. 状态管理 ===
if 'active_workflow' not in st.session_state:
    st.session_state.active_workflow = 'text' 
if 'selected_text_model_index' not in st.session_state:
    st.session_state.selected_text_model_index = 0
if 'selected_image_model_index' not in st.session_state:
    st.session_state.selected_image_model_index = None

def on_text_model_change():
    st.session_state.active_workflow = 'text'
    st.session_state.selected_image_model_index = None 

def on_image_model_change():
    st.session_state.active_workflow = 'image'
    st.session_state.selected_text_model_index = None 

# === 4. CSS 样式 ===
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    header {visibility: visible !important; background-color: transparent !important;}
    .main .block-container {padding-top: 2rem !important; padding-bottom: 2rem !important; max-width: 100% !important;}
    :root { --brand-blue: #0052D4; --brand-yellow: #FF9F43; }
    .brand-blue { color: var(--brand-blue) !important; }
    .brand-yellow { color: var(--brand-yellow) !important; }
    .brand-container { margin-bottom: 30px; text-align: center; }
    .brand-title { font-size: 32px !important; font-weight: 800 !important; letter-spacing: -0.5px; line-height: 1.3 !important; margin: 0 !important; color: var(--text-color) !important; }
    .brand-caption { font-size: 12px !important; color: var(--text-color) !important; opacity: 0.7; font-weight: 500; margin-top: 5px !important; }
    .sidebar-header { font-size: 18px !important; font-weight: 800 !important; color: var(--text-color) !important; opacity: 1.0 !important; margin-top: 30px !important; margin-bottom: 10px !important; padding-left: 8px !important; border-left: 4px solid var(--brand-yellow); line-height: 1.2; }
    .stRadio { margin-top: 0px !important; } .stRadio div[role="radiogroup"] { gap: 0px !important; }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]), div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) { flex-direction: row-reverse !important; text-align: right; }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) div[data-testid="stChatMessageContentContainer"], div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContentContainer"] { background-color: var(--secondary-background-color) !important; color: var(--text-color) !important; border: 1px solid var(--brand-blue) !important; border-radius: 12px 2px 12px 12px !important; padding: 10px 16px !important; margin-right: 10px !important; margin-left: 50px !important; box-shadow: 0 2px 8px rgba(0, 82, 212, 0.15); display: inline-block; text-align: left; }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) p, div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) p { color: var(--text-color) !important; }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="chatAvatarIcon-user"] { background-color: transparent !important; border: 1px solid var(--brand-blue) !important; color: var(--brand-blue) !important; }
    div[data-testid="stChatMessageAvatarUser"] svg, div[data-testid="chatAvatarIcon-user"] svg { fill: var(--brand-blue) !important; }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]), div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) { flex-direction: row !important; }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) div[data-testid="stChatMessageContentContainer"], div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContentContainer"] { background-color: var(--secondary-background-color) !important; border: 1px solid rgba(128, 128, 128, 0.2) !important; color: var(--text-color) !important; border-radius: 2px 12px 12px 12px !important; padding: 10px 16px !important; margin-left: 10px !important; margin-right: 50px !important; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], div.stButton > button { background-color: var(--secondary-background-color) !important; color: var(--text-color) !important; border: 1px solid rgba(128, 128, 128, 0.2) !important; }
</style>
""", unsafe_allow_html=True)

# === 5. 客户端初始化 ===
if not API_KEY or not API_BASE:
    st.error("⚠️ 未检测到配置！请设置 API_BASE 和 API_KEY")
    st.stop()

client = OpenAI(api_key=API_KEY, base_url=API_BASE)

# === 6. 流式处理 ===
def stream_wrapper(response_stream):
    for chunk in response_stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# === 7. 侧边栏 ===
with st.sidebar:
    st.markdown("""
        <div class="brand-container">
            <div class="brand-title"><span class="brand-yellow">未湃 WAPI</span><br><span class="brand-blue">AIGC 工作台</span></div>
            <div class="brand-caption">Ver 1.1 Slim | Powered by WAPI Team</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header">WAPI 大语言模型中心</div>', unsafe_allow_html=True)
    text_model_selection = st.radio("选择模型", list(TEXT_MODELS_MAP.keys()), index=st.session_state.selected_text_model_index if st.session_state.active_workflow == 'text' else None, key="text_radio", on_change=on_text_model_change, label_visibility="collapsed")
    st.markdown('<div class="sidebar-header">WAPI 视觉模型中心</div>', unsafe_allow_html=True)
    image_model_selection = st.radio("选择模型", list(IMAGE_MODELS_MAP.keys()), index=st.session_state.selected_image_model_index if st.session_state.active_workflow == 'image' else None, key="image_radio", on_change=on_image_model_change, label_visibility="collapsed")
    st.write(""); st.write("")
    if st.button("🗑️ 重置当前会话"):
        if "messages" in st.session_state: del st.session_state["messages"]
        st.rerun()

# === 8. 业务逻辑 ===

# --- A. 文本工作流 ---
if st.session_state.active_workflow == 'text':
    current_model_id = TEXT_MODELS_MAP.get(text_model_selection, list(TEXT_MODELS_MAP.values())[0])
    st.subheader(f"🤖 智能对话 - {text_model_selection}")
    st.caption(f"Engine: {current_model_id}")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "你是未湃WAPI的智能助手。请以专业、简洁且富有助益的语气进行回答。"}, {"role": "assistant", "content": f"你好！我是未湃WAPI的**{text_model_selection}**智能体。有什么工作或创意我可以帮你处理？"}]
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]): st.write(msg["content"])
    if prompt := st.chat_input("输入您的问题、指令或创作需求..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(model=current_model_id, messages=st.session_state.messages, stream=True)
                response = st.write_stream(stream_wrapper(stream))
                if response: st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e: st.error(f"请求失败: {e}")

# --- B. 图像工作流 (核心修复区域 + 新增比例/分辨率选择) ---
elif st.session_state.active_workflow == 'image':
    current_model_id = IMAGE_MODELS_MAP.get(image_model_selection, list(IMAGE_MODELS_MAP.values())[0])
    st.subheader(f"🎨 视觉生成 - {image_model_selection}")
    st.caption("未湃WAPI 图像生成引擎支持")
    col1, col2 = st.columns([1, 1.5], gap="medium")
    with col1:
        st.markdown("##### 🛠️ 生成参数")
        
        # === 新增功能：比例与分辨率选择 (两列布局) ===
        ratio_col, res_col = st.columns(2)
        
        with ratio_col:
            # 默认选中第一个 (1:1)
            selected_ratio_key = st.selectbox("📏 图片比例", list(ASPECT_RATIOS.keys()), index=0)
            
        with res_col:
            # 根据选中的比例，动态获取可用的分辨率列表
            available_resolutions = ASPECT_RATIOS[selected_ratio_key]
            selected_resolution = st.selectbox("📐 分辨率", available_resolutions)

        style_preset = st.selectbox("🎭 风格滤镜", ["✨ 原图 (无风格)", "🎞️ 电影感 (Cinematic)", "🌃 赛博朋克 (Cyberpunk)", "🖌️ 水墨国风 (Ink)", "🧸 3D皮克斯 (3D)"])
        img_prompt = st.text_area("✏️ 创意描述", height=200, placeholder="描述画面主体、场景细节、光影氛围或配色要求...")
        
        final_prompt = img_prompt
        if style_preset != "✨ 原图 (无风格)":
            style_suffix = {"🎞️ 电影感 (Cinematic)": ", cinematic lighting, 8k, realistic, shallow depth of field, movie still", "🌃 赛博朋克 (Cyberpunk)": ", cyberpunk, neon lights, futuristic city, high contrast", "🖌️ 水墨国风 (Ink)": ", traditional chinese ink painting, black and white", "🧸 3D皮克斯 (3D)": ", pixar style, 3d render, cute, soft lighting"}
            if img_prompt: final_prompt += style_suffix.get(style_preset, "")
            
        generate_btn = st.button("🎨 立即生成", type="primary", use_container_width=True)

    with col2:
        st.markdown("##### 🖼️ 结果预览")
        if generate_btn:
            if not img_prompt: st.warning("请先输入创意描述！")
            else:
                with st.spinner(f"正在请求 {image_model_selection} ({selected_resolution}) 进行绘制..."):
                    try:
                        # 1. 发起请求 (使用动态分辨率)
                        res = client.images.generate(
                            model=current_model_id,
                            prompt=final_prompt,
                            size=selected_resolution  # <--- 使用用户选中的分辨率
                        )
                        
                        image_url = None
                        
                        # 2. 尝试以标准 OpenAI 方式解析
                        if res and hasattr(res, 'data') and res.data:
                            image_url = res.data[0].url

                        # 3. 针对 z-image-turbo 的兼容性解析
                        elif hasattr(res, 'model_dump'):
                            res_dict = res.model_dump()
                            if res_dict.get("images") and isinstance(res_dict["images"], list) and len(res_dict["images"]) > 0:
                                 image_url = res_dict["images"][0].get("url")

                        # 4. 根据解析结果显示
                        if image_url:
                            st.image(image_url, use_container_width=True, caption=f"生成结果 ({selected_resolution})")
                            st.success("生成完毕！")
                            st.warning("⚠️ 图片链接具有时效性，请右键保存。")
                        else:
                            st.error(f"生成失败：API 响应格式异常，未能解析出图片地址。")
                            try: st.json(res.model_dump())
                            except: st.write(res)
                                
                    except Exception as e:
                        st.error(f"请求发生异常: {e}")
        else:
            st.info("👈 选择比例，输入描述，点击生成按钮开始创作。")
