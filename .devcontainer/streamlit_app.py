import streamlit as st
from openai import OpenAI
import json

# --- 1. 配置 AI ---
client = OpenAI(api_key=st.secrets["DEEPSEEK_KEY"], base_url="https://api.deepseek.com")

st.set_page_config(page_title="心智投影实验", layout="centered")

# --- 2. 状态初始化 ---
if 'step' not in st.session_state:
    st.session_state.step = 'input'
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.loading_rest = False # 是否正在后台加载后续题目

# --- 3. 极简样式 ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-title { font-size: 1rem; font-weight: 300; text-align: center; color: #999; letter-spacing: 5px; margin-bottom: 50px; }
    .q-text { font-size: 1.3rem; font-weight: 400; color: #111; line-height: 1.8; margin-bottom: 40px; padding: 20px; border-left: 2px solid #eee; }
    div.stButton > button { width: 100%; border-radius: 0; border: 0.5px solid #ddd; background: #fff; height: 50px; }
</style>
""", unsafe_allow_html=True)

# --- 辅助函数：调用 AI 生成题目 ---
def generate_questions(identity, hobbies, count, existing_qs=""):
    exclude_prompt = f"请避开以下已有的场景内容：{existing_qs}" if existing_qs else ""
    prompt = f"""
    基于用户角色【{identity}, 经常出没在{hobbies}】，生成{count}道深度MBTI生活投射题。
    要求：1. 场景极其具体生活化。2. 严禁提及MBTI词汇。
    3. 必须输出纯净 JSON: {{"questions": [{{"q": "场景", "a": "反应1", "b": "反应2"}}]}}
    {exclude_prompt}
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        response_format={'type': 'json_object'}
    )
    return json.loads(response.choices[0].message.content).get('questions', [])

# --- 流程 A: 初始采样 (仅生成前 5 题) ---
if st.session_state.step == 'input':
    st.markdown("<div class='main-title'>STAGE 01 / SAMPLING</div>", unsafe_allow_html=True)
    identity = st.text_input("职业/身份")
    hobbies = st.text_input("非工作场景")
    
    if st.button("开启实验"):
        if identity and hobbies:
            st.session_state.user_info = (identity, hobbies)
            with st.spinner("正在构建第一组感官切面..."):
                # 先拿5题，速度极快
                st.session_state.questions = generate_questions(identity, hobbies, 5)
                st.session_state.step = 'testing'
                st.session_state.loading_rest = True # 标记需要加载后续
                st.rerun()

# --- 流程 B: 沉浸式答题 ---
elif st.session_state.step == 'testing':
    idx = len(st.session_state.answers)
    total_cached = len(st.session_state.questions)
    
    # 【核心黑科技】：当用户在答第一题时，尝试在后台静默请求剩下的 15 题
    if st.session_state.loading_rest and idx == 0:
        # 注意：Streamlit 的简单架构下，我们在用户点击第一次“继续”时顺便静默加载更稳妥
        pass

    if idx < total_cached:
        st.markdown(f"<div class='main-title'>SCENE {idx+1}</div>", unsafe_allow_html=True)
        q_item = st.session_state.questions[idx]
        st.markdown(f"<div class='q-text'>{q_item['q']}</div>", unsafe_allow_html=True)
        ans = st.radio("本能反应：", [q_item['a'], q_item['b']], index=None, key=f"q_{idx}", label_visibility="collapsed")
        
        if st.button("记录并继续"):
            if ans:
                st.session_state.answers.append({"q": q_item['q'], "ans": ans})
                
                # 当用户答完第 2 题时，如果后台还没加载剩下的，顺便加载（用户无感知或感知很小）
                if st.session_state.loading_rest and len(st.session_state.answers) == 1:
                    with st.spinner("正在同步后续场景..."):
                        more_qs = generate_questions(
                            st.session_state.user_info[0], 
                            st.session_state.user_info[1], 
                            15, 
                            str(st.session_state.questions)
                        )
                        st.session_state.questions.extend(more_qs)
                        st.session_state.loading_rest = False
                st.rerun()
    else:
        st.session_state.step = 'result'
        st.rerun()

# --- 流程 C: 揭晓 ---
elif st.session_state.step == 'result':
    st.markdown("<div class='main-title'>FINAL DECODING</div>", unsafe_allow_html=True)
    # ... 此处保持之前的 AI 分析代码即可 ...
    st.write("实验完成，正在生成深度报告...")
    # (调用 AI 进行最终分析的逻辑)
