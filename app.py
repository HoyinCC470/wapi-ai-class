import streamlit as st
from openai import OpenAI
import os

# === 1. 基础配置 ===
API_BASE = os.getenv("API_BASE", "")
API_KEY = os.getenv("API_KEY", "")

# 模型 ID 配置
TEXT_MODELS_MAP = {
    "DeepSeek V3.2": "deepseek-ai/DeepSeek-V3.2-Exp",
    "Qwen3 14B": "Qwen/Qwen3-14B"
}
IMAGE_MODELS_MAP = {
    "可图 Kolors": "Kwai-Kolors/Kolors",
    "千问绘画": "Qwen/Qwen-Image"
}

# === 2. 页面设置 ===
st.set_page_config(
    page_title="未湃 WAPI · AIGC 工作台",
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

# === 4. 品牌旗舰版 CSS (Ver 9.6 紧凑优化) ===
st.markdown("""
<style>
    /* 全局清理 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    header {visibility: visible !important; background-color: transparent !important;}

    /* 主界面 (纯白) */
    .stApp {
        background-color: #ffffff !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 侧边栏 (极浅灰) */
    [data-testid="stSidebar"] {
        background-color: #f7f9fb !important;
        border-right: 1px solid #e5e5e5;
        padding-top: 10px !important;
    }
    [data-testid="stSidebar"] * {
        color: #333333 !important;
    }

    /* --- 品牌标题区 --- */
    .brand-container {
        margin-bottom: 20px; /* 减小底部间距 */
        text-align: center;
    }
    .brand-title {
        font-size: 32px !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        line-height: 1.3 !important;
        margin: 0 !important;
    }
    .brand-yellow { color: #FF9F43 !important; }
    .brand-blue { color: #0052D4 !important; }
    
    .brand-caption {
        font-size: 12px !important; /* 字体稍微调小一点，显得更精致 */
        color: #999999 !important;
        font-weight: 500;
        margin-top: 5px !important;
        letter-spacing: 0.5px;
    }

    /* --- 侧边栏紧凑布局优化 (关键修改) --- */
    
    /* 分组标题 */
    .sidebar-header {
        font-size: 14px;
        font-weight: 700;
        color: #555;
        margin-top: 15px;  /* 缩小上方间距 */
        margin-bottom: 5px; /* 缩小下方间距 */
        padding-left: 5px;
    }
    
    /* 强制压缩 Radio 组件的上下边距 */
    .stRadio {
        margin-top: -15px !important; 
    }
    .stRadio div[role="radiogroup"] {
        gap: 0px !important; /* 选项之间紧凑一点 */
    }
    .stRadio label {
        padding-top: 5px !important;
        padding-bottom: 5px !important;
    }

    /* --- 对话气泡 (保持不变) --- */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse !important;
        text-align: right;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContentContainer"] {
        background-color: #0052D4 !important;
        color: #ffffff !important;
        border-radius: 12px 2px 12px 12px !important;
        padding: 10px 16px !important;
        margin-right: 10px !important;
        margin-left: 50px !important;
        box-shadow: 0 2px 5px rgba(0,82,212, 0.2);
        display: inline-block;
        text-align: left;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) * {
        color: #ffffff !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) div[data-testid="chatAvatarIcon-user"] {
        background-color: #e6f0ff !important;
        color: #0052D4 !important;
    }

    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        flex-direction: row !important;
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContentContainer"] {
        background-color: #f4f6f8 !important;
        border: 1px solid #e5e5e5 !important;
        color: #1a1a1a !important;
        border-radius: 2px 12px 12px 12px !important;
        padding: 10px 16px !important;
        margin-left: 10px !important;
        margin-right: 50px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) div[data-testid="chatAvatarIcon-assistant"] {
        background-color: #f3f4f6 !important;
        color: #333333 !important;
    }

    /* 按钮 */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
    }
    div.stButton > button:hover {
        border-color: #0052D4 !important;
        color: #0052D4 !important;
    }

</style>
""", unsafe_allow_html=True)

# === 5. 客户端初始化 ===
if not API_KEY or not API_BASE:
    st.error("⚠️ 未检测到配置，请检查环境变量！")
    st.stop()

client = OpenAI(api_key=API_KEY, base_url=API_BASE)

# === 6. 流式处理函数 ===
def stream_wrapper(response_stream):
    for chunk in response_stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# === 7. 侧边栏布局 (紧凑分组版) ===
with st.sidebar:
    # 品牌区
    st.markdown("""
        <div class="brand-container">
            <div class="brand-title">
                <span class="brand-yellow">未湃 WAPI</span><br>
                <span class="brand-blue">AIGC 工作台</span>
            </div>
            <div class="brand-caption">Ver 1.0 Slim | Powered by Siliconflow</div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- 分组 1: 剧本创作 ---
    # 删除了分割线，用 CSS 控制间距
    st.markdown('<div class="sidebar-header">📝 剧本创作中心</div>', unsafe_allow_html=True)
    
    text_model_selection = st.radio(
        "剧本模型",
        list(TEXT_MODELS_MAP.keys()),
        index=0 if st.session_state.active_workflow == 'text' else None,
        key="text_radio",
        on_change=on_text_model_change,
        label_visibility="collapsed" 
    )

    # --- 分组 2: 分镜绘图 ---
    # 删除了中间的分割线，紧凑排列
    st.markdown('<div class="sidebar-header">🎨 分镜绘图工坊</div>', unsafe_allow_html=True)
    
    image_model_selection = st.radio(
        "绘图模型",
        list(IMAGE_MODELS_MAP.keys()),
        index=0 if st.session_state.active_workflow == 'image' else None,
        key="image_radio",
        on_change=on_image_model_change,
        label_visibility="collapsed"
    )
    
    # 底部稍微留点空再放清空按钮
    st.write("") 
    st.write("") 
    
    if st.button("🗑️ 重置当前会话"):
        st.session_state.messages = []
        st.rerun()

# === 8. 业务逻辑 ===

# --- A. 文本工作流 (剧本) ---
if st.session_state.active_workflow == 'text':
    current_model_id = TEXT_MODELS_MAP.get(text_model_selection, list(TEXT_MODELS_MAP.values())[0])
    
    st.subheader(f"📝 剧本创作 - {text_model_selection}")
    st.caption("由未湃WAPI智能引擎驱动")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "你是未湃WAPI的首席内容官和智能编剧助手。你的说话风格专业、富有创意，擅长影视剧本结构。"},
            {"role": "assistant", "content": f"你好！我是未湃WAPI的**{text_model_selection}**。请告诉我你想创作什么类型的故事？"}
        ]

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
                st.write(msg["content"])

    if prompt := st.chat_input("输入故事大纲..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            try:
                stream = client.chat.completions.create(
                    model=current_model_id,
                    messages=st.session_state.messages,
                    stream=True
                )
                response = st.write_stream(stream_wrapper(stream))
                
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"网络波动: {e}")

# --- B. 图像工作流 (分镜) ---
elif st.session_state.active_workflow == 'image':
    current_model_id = IMAGE_MODELS_MAP.get(image_model_selection, list(IMAGE_MODELS_MAP.values())[0])
    
    st.subheader(f"🎨 分镜绘制 - {image_model_selection}")
    st.caption("由未湃WAPI视觉引擎驱动")

    col1, col2 = st.columns([1, 1.5], gap="medium")

    with col1:
        st.markdown("##### 🛠️ 画面参数")
        style_preset = st.selectbox(
            "风格滤镜",
            ["✨ 原图 (无风格)", "🎞️ 电影感 (Cinematic)", "🌃 赛博朋克 (Cyberpunk)", "🖌️ 水墨国风 (Ink)", "🧸 3D皮克斯 (3D)"]
        )
        
        img_prompt = st.text_area("画面描述", height=200, placeholder="描述画面主体、环境、光影...")
        
        final_prompt = img_prompt
        if style_preset != "✨ 原图 (无风格)":
            style_suffix = {
                "🎞️ 电影感 (Cinematic)": ", cinematic lighting, 8k, realistic, shallow depth of field, movie still",
                "🌃 赛博朋克 (Cyberpunk)": ", cyberpunk, neon lights, futuristic city, high contrast",
                "🖌️ 水墨国风 (Ink)": ", traditional chinese ink painting, black and white, artistic, masterpiece",
                "🧸 3D皮克斯 (3D)": ", pixar style, 3d render, unreal engine 5, cute, soft lighting"
            }
            if img_prompt:
                final_prompt += style_suffix.get(style_preset, "")

        generate_btn = st.button("🎨 立即生成", type="primary", use_container_width=True)

    with col2:
        st.markdown("##### 🖼️ 实时预览")
        if generate_btn:
            if not img_prompt:
                st.warning("请先输入描述！")
            else:
                with st.spinner(f"正在请求 {image_model_selection} 绘图..."):
                    try:
                        res = client.images.generate(
                            model=current_model_id,
                            prompt=final_prompt,
                            size="1024x1024"
                        )
                        image_url = res.data[0].url
                        st.image(image_url, use_container_width=True, caption="生成结果")
                        st.success("绘制完成！")
                        st.warning("⚠️ 图片链接具有时效性，请右键保存。")
                    except Exception as e:
                        st.error(f"绘图失败: {e}\n检查OneAPI模型ID: {current_model_id}")
        else:
            st.info("👈 在左侧配置参数，点击生成按钮开始绘制。")
