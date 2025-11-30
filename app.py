import streamlit as st
from openai import OpenAI
import os

# === 配置读取 (从环境变量) ===
# 如果本地运行没有环境变量，会使用空字符串，界面会提示配置
API_BASE = os.getenv("API_BASE", "")
API_KEY = os.getenv("API_KEY", "")

# === 界面设置 ===
st.set_page_config(page_title="AI 创作工作台", page_icon="🎬", layout="wide")

# 自定义 CSS 让界面更干净
st.markdown("""
<style>
    .stApp { max-width: 1200px; margin: 0 auto; }
    .main-header { font-size: 2rem; font-weight: 700; margin-bottom: 1rem; color: #333; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎬 团队 AI 影片创作流</div>', unsafe_allow_html=True)

# === 检查配置 ===
if not API_KEY or not API_BASE:
    st.warning("⚠️ 尚未检测到 API 配置。请在 Zeabur 环境变量中设置 API_KEY 和 API_BASE。")
    st.stop()

# 初始化客户端
try:
    client = OpenAI(api_key=API_KEY, base_url=API_BASE)
except Exception as e:
    st.error(f"连接失败: {e}")
    st.stop()

# === 侧边栏 ===
with st.sidebar:
    st.header("流程选择")
    mode = st.radio("请选择工序:", ["📝 剧本/脚本创作", "🎨 分镜画面生成"])
    st.markdown("---")
    st.info("💡 提示：\n1. 剧本使用 Qwen-Turbo\n2. 画面使用 Flux.1")

# === 逻辑处理 ===

if mode == "📝 剧本/脚本创作":
    st.subheader("剧本创作助手")
    
    # 初始化聊天记录
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "我是编剧助手，请告诉我你想写什么故事？"}]

    # 显示历史记录
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # 处理输入
    if prompt := st.chat_input("输入故事大纲..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            try:
                # 强制使用千问
                stream = client.chat.completions.create(
                    model="gpt-3.5-turbo", 
                    messages=st.session_state.messages, 
                    stream=True
                )
                response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"生成出错: {e}")

elif mode == "🎨 分镜画面生成":
    st.subheader("分镜绘制 (Flux)")
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        img_prompt = st.text_area("画面描述", height=150, placeholder="例如：中国古代庭院，桃花盛开，一位少女在弹琴，电影质感，8k分辨率...")
        generate_btn = st.button("开始生成", type="primary")
    
    with col2:
        if generate_btn:
            if not img_prompt:
                st.warning("请输入描述！")
            else:
                with st.spinner("AI 正在绘图，请稍候 (约3-5秒)..."):
                    try:
                        # 强制使用 Flux (请确保您 OneAPI 里有这个名字，或者做了重定向)
                        # 如果您做过重定向 dall-e-3 -> flux，这里可以改成 "dall-e-3"
                        res = client.images.generate(
                            model="dall-e-3", 
                            prompt=img_prompt, 
                            size="1024x1024"
                        )
                        image_url = res.data[0].url
                        st.image(image_url, caption="生成预览")
                        st.success("生成成功！请右键保存图片。")
                    except Exception as e:
                        st.error(f"绘图失败: {e}\n\n请检查 OneAPI 日志或确认模型名称是否正确。")
