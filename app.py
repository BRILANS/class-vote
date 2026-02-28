import streamlit as st
import pandas as pd
import time
import random
import json
import os
from collections import Counter

# --- 설정 및 데이터 처리 함수 ---
def get_file_path(class_id): return f"data_{class_id}.json"

def load_data(class_id):
    path = get_file_path(class_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"candidates": [], "votes": [], "info": {"target": 25}}

def save_data(class_id, data):
    with open(get_file_path(class_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

st.set_page_config(page_title="학급회장 선거", layout="centered", initial_sidebar_state="collapsed")
animation_css = """
<style>
@keyframes unfold { 0% { transform: scaleY(0); opacity: 0; } 100% { transform: scaleY(1); opacity: 1; } }
.paper-box { background-color: white; border: 3px solid #ff4b4b; padding: 30px; border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); text-align: center; animation: unfold 0.8s ease-out forwards; transform-origin: top; }
</style>
"""

# --- URL 모드 ---
query_params = st.query_params
is_teacher = query_params.get("mode") == "teacher"
if 'is_teacher_mode' not in st.session_state: st.session_state.is_teacher_mode = False

if is_teacher and not st.session_state.is_teacher_mode:
    password = st.sidebar.text_input("교사 비밀번호", type="password")
    if password == "1234": st.session_state.is_teacher_mode = True; st.rerun()
    st.stop()

# ---------------------------------------------------------
# [교사 모드]
# ---------------------------------------------------------
if st.session_state.is_teacher_mode:
    st.title("👨‍🏫 선거 관리자 모드")
    class_id = st.text_input("학급 ID를 입력하세요 (예: 1-1)")
    
    if class_id:
        data = load_data(class_id)
        tab1, tab2, tab3 = st.tabs(["1. 정보 설정", "2. 후보 관리", "3. 개표 대시보드"])

        with tab1:
            target = st.number_input("투표 목표 인원", value=data["info"]["target"])
            if st.button("저장"): data["info"]["target"] = target; save_data(class_id, data)

        with tab2:
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("후보 이름")
                if st.form_submit_button("후보 추가"):
                    data["candidates"].append({"symbol": len(data["candidates"]) + 1, "name": name})
                    save_data(class_id, data); st.rerun()
            if data["candidates"]: st.dataframe(pd.DataFrame(data["candidates"]))

        with tab3:
            st.markdown(animation_css, unsafe_allow_html=True)
            st.info(f"현재 집계된 투표수: {len(data['votes'])} / {data['info']['target']}")
            
            # [수정된 개표 로직]
            if st.button("🔥 개표 시작"):
                # 개표할 때 파일을 한 번 더 확실하게 새로 읽어옴
                latest_data = load_data(class_id)
                votes = latest_data["votes"]
                
                if not votes:
                    st.error("투표된 표가 없습니다!")
                else:
                    random.shuffle(votes)
                    box = st.empty()
                    for i, vote in enumerate(votes):
                        with box.container():
                            st.markdown(f'<div class="paper-box"><h2>{i+1}번째 투표지</h2><h1>{vote}</h1></div>', unsafe_allow_html=True)
                        time.sleep(1.2) # 속도 조절
                    
                    st.balloons()
                    st.success("🎉 개표 완료!")
                    # 결과 집계
                    counts = Counter(votes)
                    winner, count = counts.most_common(1)[0]
                    st.markdown(f"## 🏆 당선자: {winner} ({count}표)")

# ---------------------------------------------------------
# [학생 모드]
# ---------------------------------------------------------
else:
    st.markdown("<style>#MainMenu {visibility: hidden;}</style>", unsafe_allow_html=True)
    st.title("🗳️ 학급회장 선거")
    class_id = st.text_input("학급 ID 입력")
    if class_id:
        data = load_data(class_id)
        if 'has_voted' not in st.session_state: st.session_state.has_voted = False
        
        if st.session_state.has_voted: st.success("✅ 투표가 완료되었습니다!")
        elif not data["candidates"]: st.warning("아직 투표가 시작되지 않았습니다.")
        else:
            selection = st.radio("후보자를 선택하세요", [c["name"] for c in data["candidates"]])
            if st.button("제출하기"):
                data["votes"].append(selection)
                save_data(class_id, data)
                st.session_state.has_voted = True; st.rerun()