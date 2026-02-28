import streamlit as st
import pandas as pd
import time
import random
from collections import Counter

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="학급회장 선거", layout="centered", initial_sidebar_state="collapsed")

# --- 2. 데이터 초기화 ---
if 'votes' not in st.session_state: st.session_state.votes = []
if 'candidates' not in st.session_state: st.session_state.candidates = []
if 'has_voted' not in st.session_state: st.session_state.has_voted = False
if 'is_counting' not in st.session_state: st.session_state.is_counting = False
if 'show_winner' not in st.session_state: st.session_state.show_winner = False
if 'show_force_button' not in st.session_state: st.session_state.show_force_button = False
if 'is_teacher_mode' not in st.session_state: st.session_state.is_teacher_mode = False
if 'election_info' not in st.session_state:
    st.session_state.election_info = {"year": 2026, "semester": 1, "grade": 1, "class": 1, "target": 25}

# --- 3. 비밀 통로 (URL 모드) ---
query_params = st.query_params

if query_params.get("mode") == "teacher":
    # 이미 인증된 상태가 아니라면
    if not st.session_state.is_teacher_mode:
        password = st.sidebar.text_input("교사 비밀번호", type="password")
        if password == "1234":
            st.session_state.is_teacher_mode = True
            st.rerun() # 비밀번호 맞으면 다시 화면을 그려서 관리자 모드로 진입
        elif password != "": # 비밀번호를 입력했는데 틀린 경우
            st.error("비밀번호가 틀렸습니다.")
            st.stop()
        else: # 아직 입력 전인 경우
            st.stop() # 아무것도 하지 말고 멈춤

# --- CSS 애니메이션 ---
animation_css = """
<style>
@keyframes unfold { 0% { transform: scaleY(0); opacity: 0; } 100% { transform: scaleY(1); opacity: 1; } }
.paper-box { background-color: white; border: 3px solid #ff4b4b; padding: 50px; border-radius: 10px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); text-align: center; animation: unfold 0.8s ease-out forwards; transform-origin: top; }
</style>
"""

# ---------------------------------------------------------
# [교사 모드]
# ---------------------------------------------------------
if st.session_state.is_teacher_mode:
    st.title("👨‍🏫 선거 관리자 모드")
    tab1, tab2, tab3 = st.tabs(["1. 정보 설정", "2. 후보 관리", "3. 개표 대시보드"])

    with tab1:
        st.session_state.election_info["year"] = st.number_input("학년도", value=2026)
        st.session_state.election_info["target"] = st.number_input("투표 목표 인원", value=25)

    with tab2:
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("후보 이름")
            gender = st.selectbox("성별", ["남", "여"])
            if st.form_submit_button("후보 추가"):
                st.session_state.candidates.append({"symbol": len(st.session_state.candidates) + 1, "name": name, "gender": gender})
                st.rerun()
        if st.session_state.candidates:
            df = pd.DataFrame(st.session_state.candidates)
            st.dataframe(df, use_container_width=True)
            if st.button("초기화"): st.session_state.candidates = []; st.rerun()

    with tab3:
        st.markdown(animation_css, unsafe_allow_html=True)
        if not st.session_state.is_counting and not st.session_state.show_winner:
            if st.button("🔥 개표 시작"):
                if len(st.session_state.votes) != st.session_state.election_info["target"]:
                    st.session_state.show_force_button = True
                else:
                    st.session_state.is_counting = True
                    st.rerun()
        if st.session_state.show_force_button:
            if st.button("⚠️ 강제 개표 진행"):
                st.session_state.is_counting = True
                st.session_state.show_force_button = False
                st.rerun()
        if st.session_state.is_counting:
            box = st.empty()
            random.shuffle(st.session_state.votes)
            for i, vote in enumerate(st.session_state.votes):
                with box.container():
                    st.markdown(f'<div class="paper-box"><h1>{vote}</h1></div>', unsafe_allow_html=True)
                time.sleep(1.0)
            st.session_state.is_counting = False
            st.session_state.show_winner = True
            st.rerun()
        if st.session_state.show_winner:
            counts = Counter(st.session_state.votes)
            winner, count = counts.most_common(1)[0]
            st.success(f"🏆 {winner} ({count}표) 당선!")

# ---------------------------------------------------------
# [학생 모드]
# ---------------------------------------------------------
else:
    st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)
    if st.session_state.has_voted:
        st.success("✅ 투표가 완료되었습니다! 잠시 기다려주세요.")
    else:
        st.title("🗳️ 학급회장 선거")
        if not st.session_state.candidates:
            st.warning("아직 투표가 시작되지 않았습니다.")
        else:
            options = [f"{c['symbol']}번 {c['name']}" for c in st.session_state.candidates]
            selection = st.radio("후보자를 선택하세요", options)
            if st.button("제출하기"):
                st.session_state.votes.append(selection)
                st.session_state.has_voted = True
                st.rerun()