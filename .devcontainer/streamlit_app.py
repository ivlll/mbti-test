import streamlit as st
from openai import OpenAI
import json

# --- 1. 配置 AI (从云端 Secrets 读取) ---
# 部署后在 Streamlit 后台设置这个 KEY
client = OpenAI(
    api_key=st.secrets["DEEPSEEK_KEY"], 
    base_url="https://api.deepseek.com"
)

st.set_page_config(page_title="心智投影实验", layout="centered")

# --- 2. 状态初始化 ---
if 'step' not in st.session_state:
    st.session_state.step = 'input'
    st.session_state.questions = []
    st.session_state.answers = []

# --- 3. 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-title { font-size: 1rem; font-weight: 300; text-align: center; color: #999; letter-spacing: 5px; margin-bottom: 50px; }
    .q-text { font-size: 1.4rem; font-weight: 400; color: #111; line-height: 1.6; margin-bottom: 40px; padding: 20px; background: #fdfdfd; border-radius: 8px; }
    div.stButton > button { width: 100%; border-radius: 0; border: 0.5px solid #ddd; background: #fff; color: #222; height: 50px; }
</style>
""", unsafe_allow_html=True)

# --- 流程控制 (保持你之前的逻辑) ---
if st.session_state.step == 'input':
    st.markdown("<div class='main-title'>STAGE 01 / SAMPLING</div>", unsafe_allow_html=True)
    identity = st.text_input("职业/身份")
    hobbies = st.text_input("非工作场景")
    if st.button("构建全场景实验"):
        if identity and hobbies:
            with st.spinner("AI 正在编撰题目..."):
                prompt = f"基于{identity}和{hobbies}生成20道MBTI生活投射题，严格JSON格式。"
                # ... (此处省略部分重复的逻辑代码，确保与你本地运行一致即可)
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={'type': 'json_object'}
                )
                data = json.loads(response.choices[0].message.content)
                st.session_state.questions = data.get('questions') or list(data.values())[0]
                st.session_state.step = 'testing'
                st.rerun()

elif st.session_state.step == 'testing':
    # ... (复制你之前的答题部分代码)
    pass 

elif st.session_state.step == 'analyzing':
    # ... (复制你之前的分析部分代码)
    pass
