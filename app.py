import streamlit as st
from openai import OpenAI
import os
import base64

# === 1. 基础配置 ===
API_BASE = os.getenv("API_BASE", "")
API_KEY = os.getenv("API_KEY", "")

# 模型配置
TEXT_MODEL = "gpt-3.5-turbo"
IMAGE_MODEL = "dall-e-3"

# === 2. 页面设置 ===
st.set_page_config(
    page_title="未湃WAPI·AIGC工作台",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === 3. Gemini 风格深度美化 CSS ===
st.markdown("""
<style>
    /* --- 全局隐藏清理 --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    
    /* 修复汉堡菜单可见性 */
    header {
        visibility: visible !important;
        background-color: transparent !important;
    }
    
    /* --- 侧边栏：Gemini 深色风格 --- */
    [data-testid="stSidebar"] {
        background-color: #1e1e1e !important; /* Gemini 深灰背景 */
        border-right: 1px solid #333333;
    }
    
    /* 侧边栏文字：强制白色/浅灰 */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        text-align: center; /* 标题居中 */
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #e0e0e0 !important;
    }
    
    /* 侧边栏输入组件美化 (适配深色背景) */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        color: #ffffff;
    }
    
    /* --- 关键：Logo 图片居中 --- */
    [data-testid="stSidebar"] [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        object-fit: contain;
    }

    /* --- 主界面优化 --- */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 聊天气泡：更现代的圆角 */
    .stChatMessage {
        background-color: transparent;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }
    /* 用户气泡强调色 */
    [data-testid="chatAvatarIcon-user"] {
        background-color: #4c8bf5 !important; /* Gemini Blue */
    }
    
    /* 按钮：Gemini 风格圆角按钮 */
    div.stButton > button {
        border-radius: 20px;
        font-weight: 600;
        border: 1px solid #444;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        border-color: #4c8bf5;
        color: #4c8bf5;
    }
</style>
""", unsafe_allow_html=True)

# === 4. 客户端初始化 ===
if not API_KEY or not API_BASE:
    st.error("⚠️ 未检测到 API 配置，请检查 Zeabur 环境变量！")
    st.stop()

client = OpenAI(api_key=API_KEY, base_url=API_BASE)

# === 5. 高级流式处理函数 ===
def stream_wrapper(response_stream):
    for chunk in response_stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# === 6. 侧边栏布局 (居中优化版) ===
with st.sidebar:
    # 1. LOGO 部分
    try:
        # 尝试读取 logo.png，宽度调大一点
        st.image("logo.png", width=140) 
    except:
        st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=80)

    # 2. 标题和版本号 (使用 HTML 强制居中)
    st.markdown("""
        <div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
            <h2 style="color: white; margin:0; font-size: 20px;">未湃WAPI·AIGC</h2>
            <p style="color: #888; font-size: 12px; margin-top: 5px;">Ver 4.4 Pro | 团队专用</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    mode = st.radio(
        "工作流选择:",
        ["📝 剧本创作中心", "🎨 分镜绘图工坊"],
        captions=["Deepseek V3.2 驱动", "Qwen Image / Flux 驱动"]
    )
    
    st.markdown("---")
    with st.expander("💡 提示词指南"):
        st.markdown("""
        **剧本：** 设定清晰的角色、冲突和结局。
        
        **分镜：** *主体 + 环境 + 风格 + 光影*
        """)
    
    st.markdown("---")
    if st.button("🗑️ 清空历史", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# === 7. 业务逻辑 ===

# --- A. 剧本创作 ---
if mode == "📝 剧本创作中心":
    st.subheader("📝 剧本创作助手")
    st.caption("由 Deepseek V3.2 提供强力推理支持")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "你好！我是未湃WAPI的智能编剧搭档。我们可以开始写大纲了吗？"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.write(msg["content"])

    if prompt := st.chat_input("输入你的创意..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            try:
                stream = client.chat.completions.create(
                    model=TEXT_MODEL,
                    messages=st.session_state.messages,
                    stream=True
                )
                response = st.write_stream(stream_wrapper(stream))
                
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
            except Exception as e:
                st.error(f"网络请求中断: {e}")

# --- B. 分镜绘制 ---
elif mode == "🎨 分镜绘图工坊":
    st.subheader("🎨 分镜绘图工坊")
    st.caption("由 Qwen image / Flux 提供图像生成支持")

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.markdown("##### 🛠️ 参数配置")
        style_preset = st.selectbox(
            "选择画面风格",
            ["无 (默认)", "电影质感 (Cinematic)", "赛博朋克 (Cyberpunk)", "吉卜力动漫 (Anime)", "水墨中国风 (Ink Style)", "3D皮克斯 (3D Render)"]
        )
        
        img_prompt = st.text_area("画面描述 (Prompt)", height=200, placeholder="例如：一位少女站在悬崖边，眺望远方的大海，背影...")
        
        final_prompt = img_prompt
        if style_preset != "无 (默认)":
            style_suffix = {
                "电影质感 (Cinematic)": ", cinematic lighting, 8k, realistic, shallow depth of field, movie still, color graded",
                "赛博朋克 (Cyberpunk)": ", cyberpunk style, neon lights, futuristic city, high contrast, ray tracing",
                "吉卜力动漫 (Anime)": ", studio ghibli style, anime art, vibrant colors, detailed background, hand drawn feel",
                "水墨中国风 (Ink Style)": ", traditional chinese ink painting, black and white, artistic, masterpiece, splashing ink",
                "3D皮克斯 (3D Render)": ", pixar style, 3d render, unreal engine 5, cute, soft lighting, clay texture"
            }
            if img_prompt:
                final_prompt += style_suffix[style_preset]

        generate_btn = st.button("✨ 开始生成画面", type="primary")
        
        if final_prompt:
            st.info(f"最终发送提示词：\n{final_prompt}")

    with col2:
        st.markdown("##### 🖼️ 画面预览")
        if generate_btn:
            if not img_prompt:
                st.warning("请先输入画面描述！")
            else:
                with st.spinner("AI 画师正在绘制中..."):
                    try:
                        res = client.images.generate(
                            model=IMAGE_MODEL,
                            prompt=final_prompt,
                            size="1024x1024"
                        )
                        image_url = res.data[0].url
                        
                        st.image(image_url, use_container_width=True, caption="生成结果")
                        st.success("生成完毕！")
                        st.warning("⚠️ 生成图片非永久保留，请尽快保存到本地。")
                        
                    except Exception as e:
                        st.error(f"绘图失败: {e}")
