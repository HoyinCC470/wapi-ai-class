import streamlit as st
from openai import OpenAI
import os

# ================= 配置区域 =================
# 建议在 Sealos 环境变量里设置，这里作为保底
API_BASE = os.getenv("API_BASE", "https://您的OneAPI域名.zeabur.app/v1")
API_KEY = os.getenv("API_KEY", "sk-您的OneAPI令牌")

# 模型名称 (必须要和 OneAPI 里添加的一致)
TEXT_MODEL = "qwen-turbo"
IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell" # 或者 dall-e-3 (如果您做了重定向)
# ===========================================

st.set_page_config(page_title="AI 影片创作流", layout="wide")
st.title("🎬 AI 影片制作课程工作台")

# 初始化客户端
client = OpenAI(api_key=API_KEY, base_url=API_BASE)

# 侧边栏设置
with st.sidebar:
    st.info(f"当前接入：OneAPI \n\n 模型：{TEXT_MODEL} | {IMAGE_MODEL}")
    st.markdown("---")
    st.markdown("### 💡 使用指南")
    st.markdown("1. 先用 **编剧** 写故事")
    st.markdown("2. 复制画面描述到 **分镜**")
    st.markdown("3. 生成图片保存")

# 创建三个标签页
tab1, tab2, tab3 = st.tabs(["📝 剧本创作", "🎨 分镜绘制", "🎥 视频生成"])

# --- Tab 1: 文本对话 ---
with tab1:
    st.subheader("剧本与脚本创作")
    
    # 初始化聊天记录
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "我是通义千问，请告诉我你想拍什么故事？"}]

    # 显示历史消息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 输入框
    if prompt := st.chat_input("输入故事大纲..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=TEXT_MODEL,
                messages=st.session_state.messages,
                stream=True
            )
            response = st.write_stream(stream)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- Tab 2: 文生图 ---
with tab2:
    st.subheader("分镜画面生成 (Flux/Kolors)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        img_prompt = st.text_area("画面描述 (提示词)", height=150, placeholder="例如：赛博朋克风格的街道，霓虹灯，雨夜，高清...")
        generate_btn = st.button("生成画面", type="primary")
    
    with col2:
        if generate_btn and img_prompt:
            with st.spinner("正在绘制分镜，请稍候..."):
                try:
                    # 调用生图 API
                    response = client.images.generate(
                        model=IMAGE_MODEL,
                        prompt=img_prompt,
                        size="1024x1024",
                        n=1
                    )
                    image_url = response.data[0].url
                    st.image(image_url, caption="生成结果", use_column_width=True)
                    st.success("生成成功！右键可保存图片。")
                except Exception as e:
                    st.error(f"生成失败：{e}")

# --- Tab 3: 视频 (预留) ---
with tab3:
    st.subheader("图生视频 / 文生视频")
    st.info("⚠️ 视频生成接口需要单独接入 (如 Kling/Runway)，目前 OneAPI 对视频支持尚不完善。建议学生使用生成的图片，去可灵/即梦官网生成视频。")