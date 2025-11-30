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
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === 3. 注入自定义 CSS ===
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    h1 { color: #1E1E1E; font-weight: 700; letter-spacing: -1px; }
    section[data-testid="stSidebar"] { background-color: #f7f9fa; border-right: 1px solid #e0e0e0; }
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; transition: all 0.2s; }
    .stChatMessage { border-radius: 10px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# === 4. 初始化客户端 ===
if not API_KEY or not API_BASE:
    st.error("⚠️ 未检测到 API 配置，请检查 Zeabur 环境变量！")
    st.stop()

client = OpenAI(api_key=API_KEY, base_url=API_BASE)

# === 5. 侧边栏设计 ===
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=60)
    st.title("未湃WAPI·AIGC工作台")
    st.caption("Ver 3.2 Pro | 极致丝滑版")
    st.markdown("---")
    
    mode = st.radio(
        "选择工作流:",
        ["📝 剧本创作中心", "🎨 分镜绘图工坊"],
        captions=["由 Deepseek V3.2 模型提供支持", "由 Qwen image 1.0 提供支持"]
    )
    
    st.markdown("---")
    if st.button("🗑️ 清空对话历史", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# === 6. 主逻辑区域 ===

if mode == "📝 剧本创作中心":
    st.header("📝 剧本创作助手")
    st.caption("由 Deepseek V3.2 提供强力推理支持")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "你好！我是未湃WAPI的智能编剧搭档。我们可以开始写大纲了吗？"}]

    # 渲染历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.write(msg["content"])

    # 处理输入
    if prompt := st.chat_input("输入你的创意..."):
        # 1. 显示用户输入
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)

        # 2. AI 生成 (使用 write_stream 实现丝滑效果)
        with st.chat_message("assistant", avatar="🤖"):
            try:
                stream = client.chat.completions.create(
                    model=TEXT_MODEL,
                    messages=st.session_state.messages,
                    stream=True
                )
                # --- 关键修改：使用 st.write_stream 代替手动循环 ---
                # 这个函数会自动处理缓冲和平滑渲染，彻底告别卡顿
                response = st.write_stream(stream)
                # ----------------------------------------------
                
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"生成失败: {e}")

elif mode == "🎨 分镜绘图工坊":
    st.header("🎨 分镜绘图工坊")
    st.caption("由 Qwen image 1.0 提供图像生成支持")

    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.subheader("🛠️ 参数设置")
        style_preset = st.selectbox(
            "选择画面风格",
            ["无 (默认)", "电影质感 (Cinematic)", "赛博朋克 (Cyberpunk)", "吉卜力动漫 (Anime)", "水墨中国风 (Ink Style)", "3D皮克斯 (3D Render)"]
        )
        
        img_prompt = st.text_area("画面描述 (Prompt)", height=200, placeholder="例如：一位少女站在悬崖边，眺望远方的大海，背影...")
        
        final_prompt = img_prompt
        if style_preset != "无 (默认)":
            style_suffix = {
                "电影质感 (Cinematic)": ", cinematic lighting, 8k, realistic, shallow depth of field, movie still",
                "赛博朋克 (Cyberpunk)": ", cyberpunk style, neon lights, futuristic city, high contrast",
                "吉卜力动漫 (Anime)": ", studio ghibli style, anime art, vibrant colors, detailed background",
                "水墨中国风 (Ink Style)": ", traditional chinese ink painting, black and white, artistic, masterpiece",
                "3D皮克斯 (3D Render)": ", pixar style, 3d render, unreal engine 5, cute, soft lighting"
            }
            if img_prompt:
                final_prompt += style_suffix[style_preset]

        generate_btn = st.button("✨ 开始生成画面", type="primary")
        
        if final_prompt:
            st.info(f"实际发送的提示词：\n{final_prompt}")

    with col2:
        st.subheader("🖼️ 画面预览")
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
                        st.image(image_url, use_column_width=True, caption="生成结果")
                        st.success("生成完毕！")
                        st.markdown(f"[📥 点击这里在新窗口打开图片]({image_url})")
                    except Exception as e:
                        st.error(f"绘图失败: {e}")
