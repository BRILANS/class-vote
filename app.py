import streamlit as st
import pandas as pd
import json
import os
import time
import random
from collections import Counter

# --- 설정 및 CSS ---
animation_css = """
<style>
@keyframes unfold { 0% { transform: scaleY(0); opacity: 0; } 100% { transform: scaleY(1); opacity: 1; } }
.paper-box { background-color: white; border: 3px solid #ff4b4b; padding: 30px; border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); text-align: center; animation: unfold 0.8s ease-out forwards; transform-origin: top; }
.winner-card { background-color: #fff8e1; border: 5px solid #ffc107; padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
</style>
"""

# --- 데이터 처리 함수 ---
def get_file_path(class_id): return f"data_{class_id}.json"

def load_data(class_id):
    path = get_file_path(class_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"candidates": [], "votes": [], "info": {"school": "OO중학교", "year": 2026, "semester": 1, "grade": 1, "class": 1, "type": "학급회장", "target": 25}}

def save_data(class_id, data):
    with open(get_file_path(class_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

st.set_page_config(page_title="학급회장 선거", layout="centered", initial_sidebar_state="collapsed")
st.markdown(animation_css, unsafe_allow_html=True)

# --- 상태 초기화 ---
if 'is_teacher_mode' not in st.session_state: st.session_state.is_teacher_mode = False
if 'counting_finished' not in st.session_state: st.session_state.counting_finished = False
if 'show_winner_screen' not in st.session_state: st.session_state.show_winner_screen = False

# --- 인증 처리 ---
query_params = st.query_params
is_teacher = query_params.get("mode") == "teacher"

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
            st.session_state.school = st.text_input("학교 이름", value=data["info"].get("school", "OO중학교"))
            st.session_state.type = st.text_input("선거 구분 (예: 학급회장)", value=data["info"].get("type", "학급회장"))
            col1, col2 = st.columns(2)
            st.session_state.grade = col1.number_input("학년", value=data["info"].get("grade", 1))
            st.session_state.class_num = col2.number_input("반", value=data["info"].get("class", 1))
            st.session_state.target = st.number_input("목표 투표 인원", value=data["info"].get("target", 25))
            if st.button("정보 저장"):
                data["info"].update({"school": st.session_state.school, "type": st.session_state.type, "grade": st.session_state.grade, "class": st.session_state.class_num, "target": st.session_state.target})
                save_data(class_id, data); st.success("저장 완료!")

        with tab2:
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("후보 이름")
                if st.form_submit_button("후보 추가"):
                    data["candidates"].append({"name": name})
                    save_data(class_id, data); st.rerun()
            if data["candidates"]:
                del_name = st.selectbox("삭제할 후보 선택", [c['name'] for c in data["candidates"]])
                if st.button("선택한 후보 삭제"):
                    data["candidates"] = [c for c in data["candidates"] if c['name'] != del_name]
                    save_data(class_id, data); st.rerun()

        with tab3:
            # 🔄 실시간 확인 버튼
            if st.button("🔄 현재 투표 인원 확인하기"):
                data = load_data(class_id) # 최신 데이터 다시 불러오기
            
            st.info(f"현재 집계된 투표수: {len(data['votes'])} / {data['info']['target']}")
            
            if st.button("🔄 투표 전체 초기화"): 
                data["votes"] = []; save_data(class_id, data)
                st.session_state.counting_finished = False
                st.session_state.show_winner_screen = False
                st.rerun()
            
            if st.button("🔥 개표 시작"):
                st.session_state.counting_finished = False
                st.session_state.show_winner_screen = False
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
                        time.sleep(1.0)
                    st.balloons()
                    st.session_state.counting_finished = True
                    st.rerun()
            
            if st.session_state.counting_finished:
                st.success("🎉 개표 완료!")
                if st.button("당선자 확인하기"):
                    st.session_state.show_winner_screen = True
                    st.rerun()

            if st.session_state.show_winner_screen:
                counts = Counter(data["votes"])
                winner_name, count = counts.most_common(1)[0]
                candidates_list = [c['name'] for c in data["candidates"]]
                winner_idx = candidates_list.index(winner_name) + 1
                
                st.markdown(f"""
                <div class="winner-card">
                    <h1>당선을 축하합니다!</h1>
                    <br>
                    <h1>기호 {winner_idx}번 {winner_name}</h1>
                    <br>
                    <h2>({count}표)</h2>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# [학생 모드]
# ---------------------------------------------------------
else:
    st.markdown("<style>#MainMenu {visibility: hidden;}</style>", unsafe_allow_html=True)
    class_id = st.text_input("학급 ID 입력")
    if class_id:
        data = load_data(class_id)
        info = data["info"]
        st.title(f"🗳️ {info['school']} {info['grade']}학년 {info['class']}반 {info['type']} 선거")
        
        if 'has_voted' not in st.session_state: st.session_state.has_voted = False
        if st.session_state.has_voted: st.success("✅ 투표가 완료되었습니다!")
        elif not data["candidates"]: st.warning("아직 투표가 시작되지 않았습니다.")
        else:
            selection = st.radio("후보자를 선택하세요", [c["name"] for c in data["candidates"]])
            if st.button("제출하기"):
                data["votes"].append(selection)
                save_data(class_id, data)
                st.session_state.has_voted = True; st.rerun()