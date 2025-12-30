import streamlit as st
from openai import OpenAI
import json
import time

# --- 1. 配置 AI ---
client = OpenAI(api_key=st.secrets["DEEPSEEK_KEY"], base_url="https://api.deepseek.com")

st.set_page_config(page_title="心智投影实验 2.0", layout="centered")

# --- 2. 状态初始化 ---
if 'step' not in st.session_state:
    st.session_state.step = 'input'
    st.session_state.questions = []
    st.session_state.answers = []

# --- 3. 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-title { font-size: 0.9rem; font-weight: 300; text-align: center; color: #999; letter-spacing: 4px; margin-bottom: 40px; }
    .q-text { font-size: 1.3rem; font-weight: 400; color: #111; line-height: 1.8; margin-bottom: 40px; padding: 25px; background: #fafafa; border-radius: 4px; }
    div.stButton > button { width: 100%; border-radius: 0; border: 0.5px solid #ddd; background: #fff; height: 50px; transition: 0.3s; }
    div.stButton > button:hover { border-color: #000; background: #fdfdfd; }
    .stProgress > div > div > div > div { background-color: #333; }
</style>
""", unsafe_allow_html=True)

# --- 逻辑 A: 身份输入与带进度条的出题 ---
if st.session_state.step == 'input':
    st.markdown("<div class='main-title'>STAGE 01 / SAMPLING</div>", unsafe_allow_html=True)
    identity = st.text_input("当前职业/主要身份")
    hobbies = st.text_input("常出没的非工作场景")
    
    if st.button("开始构建实验场景"):
        if identity and hobbies:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 模拟进度反馈，提升用户期待感
            status_text.text("正在连接心智引擎...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            status_text.text(f"正在编撰符合 {identity} 语境的生活切片...")
            progress_bar.progress(30)
            
            # 调用 AI 生成题目 (缩减为12题以提升速度)
            try:
                prompt = f"基于角色【{identity}, {hobbies}】生成12道深度MBTI生活化投射题。JSON格式: {{"questions": [{{"q": "场景", "a": "反应A", "b": "反应B"}}]}}"
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={'type': 'json_object'}
                )
                
                status_text.text("场景渲染完成，正在同步实验数据...")
                progress_bar.progress(80)
                
                data = json.loads(response.choices[0].message.content)
                st.session_state.questions = data.get('questions') or list(data.values())[0]
                
                progress_bar.progress(100)
                status_text.text("实验开启。")
                time.sleep(0.5)
                
                st.session_state.step = 'testing'
                st.rerun()
            except Exception as e:
                st.error(f"构建失败: {e}")
        else:
            st.warning("请填入关键信息。")

# --- 逻辑 B: 沉浸式答题 ---
elif st.session_state.step == 'testing':
    idx = len(st.session_state.answers)
    total = len(st.session_state.questions)
    
    if idx < total:
        st.markdown(f"<div class='main-title'>SCENE {idx+1} / {total}</div>", unsafe_allow_html=True)
        q_item = st.session_state.questions[idx]
        st.markdown(f"<div class='q-text'>{q_item['q']}</div>", unsafe_allow_html=True)
        
        ans = st.radio("你的直觉反应：", [q_item['a'], q_item['b']], index=None, key=f"q_{idx}", label_visibility="collapsed")
        
        if st.button("记录并进入下一场景"):
            if ans:
                st.session_state.answers.append({"q": q_item['q'], "ans": ans})
                st.rerun()
    else:
        st.session_state.step = 'result'
        st.rerun()

# --- 逻辑 C: 最终揭晓 (打字机模式，消除等待感) ---
elif st.session_state.step == 'result':
    st.markdown("<div class='main-title'>FINAL DECODING / 最终揭晓</div>", unsafe_allow_html=True)
    
    report_placeholder = st.empty()
    full_report = ""
    
    # 构建分析指令
    analysis_prompt = f"实验记录：{json.dumps(st.session_state.answers, ensure_ascii=False)}。请给出MBTI类型、称号及深度性格分析。风格要冷峻、极简、有穿透力。"
    
    try:
        # 使用 stream=True 实时获取输出
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": analysis_prompt}],
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                chunk_text = chunk.choices[0].delta.content
                full_report += chunk_text
                # 动态刷新页面内容，模拟打字机效果
                report_placeholder.markdown(full_report + " ▌")
        
        report_placeholder.markdown(full_report) # 打印完成，移除光标
        
        if st.button("重启实验"):
            st.session_state.step = 'input'
            st.session_state.answers = []
            st.rerun()
            
    except Exception as e:
        st.error(f"解析失败: {e}")
