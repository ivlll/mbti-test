import streamlit as st
from openai import OpenAI
import json
import time

# --- 1. 配置 AI (从云端 Secrets 读取) ---
try:
    client = OpenAI(
        api_key=st.secrets["DEEPSEEK_KEY"], 
        base_url="https://api.deepseek.com"
    )
except Exception as e:
    st.error("未检测到 API Key，请在 Streamlit 管理后台设置 Secrets。")

st.set_page_config(page_title="心智投影实验 2.0", layout="centered")

# --- 2. 状态初始化 ---
if 'step' not in st.session_state:
    st.session_state.step = 'input'
    st.session_state.questions = []
    st.session_state.answers = []

# --- 3. 极简 UI 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-title { font-size: 0.9rem; font-weight: 300; text-align: center; color: #999; letter-spacing: 4px; margin-bottom: 40px; text-transform: uppercase; }
    .q-text { font-size: 1.3rem; font-weight: 400; color: #111; line-height: 1.8; margin-bottom: 40px; padding: 25px; background: #fafafa; border-radius: 4px; border-left: 3px solid #eee; }
    div.stButton > button { width: 100%; border-radius: 0; border: 0.5px solid #ddd; background: #fff; height: 50px; transition: 0.3s; font-size: 1rem; }
    div.stButton > button:hover { border-color: #000; background: #fdfdfd; }
    .stProgress > div > div > div > div { background-color: #111; }
    input { border-radius: 0 !important; }
</style>
""", unsafe_allow_html=True)

# --- 流程 A: 身份输入与带进度条的出题 ---
if st.session_state.step == 'input':
    st.markdown("<div class='main-title'>STAGE 01 / SAMPLING</div>", unsafe_allow_html=True)
    identity = st.text_input("描述你的职业或核心身份", placeholder="例如：在大城市独居的插画师")
    hobbies = st.text_input("描述一个你经常出现的非工作场景", placeholder="例如：深夜的便利店、Livehouse、或是安静的图书馆")
    
    if st.button("构建实验场景"):
        if identity and hobbies:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 模拟进度反馈，提升用户期待感
            status_text.text("正在接入心智投影协议...")
            progress_bar.progress(15)
            time.sleep(0.4)
            
            status_text.text(f"正在基于 {identity} 的视角编撰生活切片...")
            progress_bar.progress(40)
            
            # 调用 AI 生成题目 (缩减为12题以极大提升响应速度)
            try:
                # 修复了大括号转义问题
                prompt = (
                    f"基于角色【{identity}, {hobbies}】生成12道深度MBTI生活化投射题。"
                    f"要求场景极其生活化且具体。必须输出严格的JSON格式，结构如下：{{\"questions\": [ {{\"q\": \"场景描述\", \"a\": \"做法一\", \"b\": \"做法二\"}} ]}}"
                )
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={'type': 'json_object'}
                )
                
                status_text.text("场景渲染完成，正在同步心智数据...")
                progress_bar.progress(85)
                
                raw_json = response.choices[0].message.content
                data = json.loads(raw_json)
                st.session_state.questions = data.get('questions') or list(data.values())[0]
                
                progress_bar.progress(100)
                status_text.text("同步成功。")
                time.sleep(0.5)
                
                st.session_state.step = 'testing'
                st.rerun()
            except Exception as e:
                st.error(f"实验启动失败，请检查网络或配置: {e}")
        else:
            st.warning("请补全身份信息，以便 AI 构思场景。")

# --- 流程 B: 沉浸式答题 (不显示性格暗示) ---
elif st.session_state.step == 'testing':
    idx = len(st.session_state.answers)
    total = len(st.session_state.questions)
    
    if idx < total:
        st.markdown(f"<div class='main-title'>SCENE {idx+1} / {total}</div>", unsafe_allow_html=True)
        q_item = st.session_state.questions[idx]
        st.markdown(f"<div class='q-text'>{q_item['q']}</div>", unsafe_allow_html=True)
        
        # index=None 强制用户必须点击，不能默认选第一个
        ans = st.radio("你的直觉反应：", [q_item['a'], q_item['b']], index=None, key=f"q_{idx}", label_visibility="collapsed")
        
        st.write("")
        if st.button("进入下一个切面"):
            if ans:
                st.session_state.answers.append({"q": q_item['q'], "ans": ans})
                st.rerun()
            else:
                st.info("请跟随本能做出选择。")
    else:
        st.session_state.step = 'result'
        st.rerun()

# --- 流程 C: 最终揭晓 (打字机流式输出) ---
elif st.session_state.step == 'result':
    st.markdown("<div class='main-title'>FINAL DECODING / 最终揭晓</div>", unsafe_allow_html=True)
    
    report_placeholder = st.empty()
    full_report = ""
    
    # 构建深度分析指令
    analysis_prompt = (
        f"用户画像：{identity}。实验记录：{json.dumps(st.session_state.answers, ensure_ascii=False)}。"
        "任务：1. 揭晓其MBTI类型及浪漫化称号。2. 进行深度心理学性格解构。3. 指出其在生活中的潜在盲点。风格：极简、冷峻、穿透力。使用Markdown排版。"
    )
    
    try:
        # 使用 stream=True 实时获取输出，消除等待感
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": analysis_prompt}],
            stream=True
        )
        
        # 模拟打字机效果
        for chunk in response:
            if chunk.choices[0].delta.content:
                chunk_text = chunk.choices[0].delta.content
                full_report += chunk_text
                report_placeholder.markdown(full_report + " ▌")
        
        report_placeholder.markdown(full_report) # 移除光标
        
        st.write("---")
        if st.button("开启新的采样"):
            st.session_state.step = 'input'
            st.session_state.answers = []
            st.rerun()
            
    except Exception as e:
        st.error(f"解析失败: {e}")
