import streamlit as st
from openai import OpenAI
import json

# --- 1. 配置 AI ---
DEEPSEEK_KEY = "sk-84830c1ccb85464aa14f40c9f82c9020" 
client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")

st.set_page_config(page_title="心智投影实验", layout="centered")

# --- 2. 状态初始化 ---
if 'step' not in st.session_state:
    st.session_state.step = 'input'
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.user_profile = ""

# --- 3. 极简 UI 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-title { font-size: 1rem; font-weight: 300; text-align: center; color: #999; letter-spacing: 5px; margin-bottom: 50px; }
    .q-text { font-size: 1.4rem; font-weight: 400; color: #111; line-height: 1.6; margin-bottom: 40px; text-align: left; padding: 20px; background: #fdfdfd; border-radius: 8px; }
    div.stButton > button { width: 100%; border-radius: 0; border: 0.5px solid #ddd; background: #fff; color: #222; height: 50px; }
    .stRadio > label { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 流程 A: 身份采样 & 动态生成题库 ---
if st.session_state.step == 'input':
    st.markdown("<div class='main-title'>STAGE 01 / SAMPLING</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.selectbox("年龄层次", ["18-24", "25-34", "35-49", "50+"])
        env = st.selectbox("生活环境", ["一线城市", "二三线城市", "海外/其他"])
    with col2:
        identity = st.text_input("职业/身份", placeholder="如: 建筑设计师")
        hobbies = st.text_input("非工作场景", placeholder="如: 经常去livehouse")

    if st.button("构建全场景实验"):
        if not identity or not hobbies:
            st.warning("请填写完整信息，以便 AI 编织场景。")
        else:
            with st.spinner("AI 正在根据您的背景编撰 20 道生活切片题目..."):
                user_ctx = f"年龄{age}, 身份{identity}, 经常出没在{hobbies}, 环境{env}"
                st.session_state.user_profile = user_ctx
                
                # 强化 JSON 稳定性 Prompt
                prompt = f"""
                你是一个资深的心理学家。基于用户画像【{user_ctx}】，生成20道深度MBTI生活化投射题。
                要求：
                1. 场景必须极其生活化，涵盖：独处、意外、社交、感官审美。
                2. 禁止出现MBTI、倾向、性格等专业词汇。
                3. 必须输出纯净的 JSON 格式，结构如下：
                {{"questions": [{{"q": "场景描述", "a": "做法一", "b": "做法二"}}]}}
                """
                try:
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}],
                        response_format={'type': 'json_object'}
                    )
                    raw_content = response.choices[0].message.content
                    data = json.loads(raw_content)
                    
                    # 稳健获取列表
                    if 'questions' in data:
                        st.session_state.questions = data['questions']
                    elif isinstance(data, list):
                        st.session_state.questions = data
                    else:
                        st.session_state.questions = list(data.values())[0]
                        
                    st.session_state.step = 'testing'
                    st.rerun()
                except Exception as e:
                    st.error(f"实验启动失败。可能原因：API余额不足或网络波动。具体报错: {str(e)}")

# --- 流程 B: 沉浸式答题 ---
elif st.session_state.step == 'testing':
    idx = len(st.session_state.answers)
    total = len(st.session_state.questions)
    
    if idx < total:
        st.markdown(f"<div class='main-title'>SCENE {idx+1} / {total}</div>", unsafe_allow_html=True)
        q_item = st.session_state.questions[idx]
        
        st.markdown(f"<div class='q-text'>{q_item['q']}</div>", unsafe_allow_html=True)
        ans = st.radio("你的本能反应：", [q_item['a'], q_item['b']], index=None, key=f"q_{idx}")
        
        st.write("---")
        if st.button("记录并继续"):
            if ans:
                st.session_state.answers.append({"q": q_item['q'], "ans": ans})
                st.rerun()
            else:
                st.info("请选择一个最接近你瞬间直觉的选择。")
    else:
        st.session_state.step = 'analyzing'
        st.rerun()

# --- 流程 C: AI 深度报告 ---
elif st.session_state.step == 'analyzing':
    st.markdown("<div class='main-title'>FINAL DECODING</div>", unsafe_allow_html=True)
    with st.spinner("正在从 20 个瞬间中还原您的真实心智地图..."):
        analysis_prompt = f"""
        用户背景：{st.session_state.user_profile}
        实验回答：{json.dumps(st.session_state.answers, ensure_ascii=False)}
        任务：
        1. 给出 MBTI 类型及一个浪漫的称号。
        2. 深度解析：指出用户的性格在“职业面具”与“真实本我”之间的潜在张力。
        3. 盲点：指出由于这种性格，他在{st.session_state.user_profile}这种背景下最容易忽视的事。
        4. 语言风格：冷静、精准、具有穿透力。使用 Markdown。
        """
        try:
            res = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            st.markdown(res.choices[0].message.content)
            
            if st.button("重新采样"):
                st.session_state.step = 'input'
                st.session_state.answers = []
                st.rerun()
        except Exception as e:
            st.error(f"报告生成失败: {str(e)}")