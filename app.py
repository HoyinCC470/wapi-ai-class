import streamlit as st
from openai import OpenAI
import os

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

# === 3. 深度美化 CSS ===
st.markdown("""
<style>
    /* 1. 隐藏多余元素，保留 Header 以修复汉堡菜单 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    
    header {
        visibility: visible !important;
        background-color: transparent !important;
    }
    
    /* 2. 全局字体与背景优化 */
    .stApp {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* 3. 侧边栏强制配色 */
    [data-testid="stSidebar"] {
        background-color: #f5f7f9 !important; 
        border-right: 1px solid #e0e0e0;
    }
    
    /* 4. 侧边栏文字颜色强制修正 */
    [data-testid="stSidebar"] * {
        color: #333333 !important; 
    }
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
        color: #333333 !important;
        background-color: #ffffff !important;
    }

    /* 5. 聊天气泡美化 */
    .stChatMessage {
        background-color: transparent;
        border-radius: 10px;
        padding: 10px;
    }
    [data-testid="chatAvatarIcon-user"] {
        background-color: #4F46E5 !important;
    }
    
    /* 6. 按钮样式增强 */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
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

# === 6. 侧边栏布局 (Logo 修改处) ===
with st.sidebar:
    # --- 修改开始: 尝试读取本地 Logo，如果没有则使用默认图标 ---
    try:
        # 尝试加载您上传的 logo.png，宽度设为 150 看起来更大气
        st.image("logo.png", width=150) 
    except:
        # 如果您还没上传 logo.png，就显示这个默认的
        st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    # --- 修改结束 ---

    st.markdown("## 未湃WAPI·AIGC")
    st.caption("Ver 4.3 Brand | 团队专用")
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
        
        **分镜：** *公式：主体 + 环境 + 风格 + 光影* 例：赛博朋克街道，雨夜，霓虹灯，电影感
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
