import streamlit as st
import pandas as pd
import time
import random
from collections import Counter

# --- 설정 ---
st.set_page_config(page_title="학급회장 선거", layout="centered")

# --- CSS ---
animation_css = """
<style>
@keyframes unfold {
    0% { transform: scaleY(0); opacity: 0; }
    100% { transform: scaleY(1); opacity: 1; }
}
.paper-box {
    background-color: white;
    border: 3px solid #ff4b4b;
    padding: 50px;
    border-radius: 10px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    text-align: center;
    animation: unfold 0.8s ease-out forwards;
    transform-origin: top;
}
</style>
"""

# --- 상태 초기화 ---
if 'votes' not in st.session_state: st.session_state.votes = []
if 'candidates' not in st.session_state: st.session_state.candidates = []
if 'has_voted' not in st.session_state: st.session_state.has_voted = False
if 'show_winner' not in st.session_state: st.session_state.show_winner = False
if 'is_counting' not in st.session_state: st.session_state.is_counting = False
if 'show_force_button' not in st.session_state: st.session_state.show_force_button = False
if 'election_info' not in st.session_state:
    st.session_state.election_info = {"year": 2026, "semester": 1, "grade": 1, "class": 1, "target": 25}

# --- 사이드바 ---
menu = st.sidebar.radio("접속 모드", ["학생 (투표)", "교사 (관리/개표)"])

# ---------------------------------------------------------
# [교사 모드]
# ---------------------------------------------------------
if menu == "교사 (관리/개표)":
    st.title("👨‍🏫 선거 관리자 모드")
    tab1, tab2, tab3 = st.tabs(["1. 정보 설정", "2. 후보 관리", "3. 개표 대시보드"])

    with tab1:
        st.subheader("선거 기본 정보")
        col1, col2 = st.columns(2)
        st.session_state.election_info["year"] = col1.number_input("학년도", value=2026)
        st.session_state.election_info["semester"] = col2.number_input("학기", value=1)
        col3, col4 = st.columns(2)
        st.session_state.election_info["grade"] = col3.number_input("학년", value=1)
        st.session_state.election_info["class"] = col4.number_input("반", value=1)
        st.session_state.election_info["target"] = st.number_input("투표 목표 인원", value=25)

    with tab2:
        st.subheader("후보자 등록 및 수정")
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("후보 이름")
            gender = st.selectbox("성별", ["남", "여"])
            if st.form_submit_button("후보 추가"):
                new_symbol = len(st.session_state.candidates) + 1
                st.session_state.candidates.append({"symbol": new_symbol, "name": name, "gender": gender})
                st.rerun()
        
        if st.session_state.candidates:
            df = pd.DataFrame(st.session_state.candidates)
            df = df.rename(columns={'symbol': '기호', 'name': '이름', 'gender': '성별'})
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            del_name = st.selectbox("삭제할 후보 선택", [c['name'] for c in st.session_state.candidates])
            if st.button("선택한 후보 삭제"):
                st.session_state.candidates = [c for c in st.session_state.candidates if c['name'] != del_name]
                for i, c in enumerate(st.session_state.candidates): c['symbol'] = i + 1
                st.rerun()

    with tab3:
        st.subheader("개표 진행")
        st.info(f"현재 투표수: {len(st.session_state.votes)} / {st.session_state.election_info['target']}")
        st.markdown(animation_css, unsafe_allow_html=True)

        # 1단계: 개표 시작 버튼
        if not st.session_state.is_counting and not st.session_state.show_winner:
            if st.button("🔥 개표 시작"):
                if len(st.session_state.votes) != st.session_state.election_info['target']:
                    st.session_state.show_force_button = True # 경고창 띄우기 위해 플래그 설정
                else:
                    st.session_state.is_counting = True
                    st.rerun()
        
        # 강제 개표 버튼 (별도로 분리)
        if st.session_state.show_force_button:
            st.warning("⚠️ 인원수가 다릅니다!")
            if st.button("그래도 강제 개표 진행하기"):
                st.session_state.is_counting = True
                st.session_state.show_force_button = False
                st.rerun()

        # 2단계: 실제 개표 루프
        if st.session_state.is_counting:
            progress = st.progress(0)
            box = st.empty()
            random.shuffle(st.session_state.votes)
            
            for i, vote in enumerate(st.session_state.votes):
                progress.progress((i + 1) / len(st.session_state.votes))
                with box.container():
                    st.markdown(f"""
                    <div class="paper-box">
                        <h2 style="color: #666; font-size: 20px;">🗳️ {i+1}번째 투표지 개표...</h2>
                        <h1 style="font-size: 50px;">{vote}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                time.sleep(1.0)
            
            st.balloons()
            st.success("🎉 개표 종료!")
            st.session_state.is_counting = False
            st.session_state.show_winner = True
            st.rerun()

        # 3단계: 결과 확인
        if st.session_state.show_winner and st.session_state.votes:
            if st.button("🏆 결과 확인하기", type="primary"):
                counts = Counter(st.session_state.votes)
                winner, count = counts.most_common(1)[0]
                st.markdown(f"""
                <div style="border: 5px solid #ffc107; padding: 40px; border-radius: 20px; text-align: center; background-color: #fff8e1;">
                    <h1 style="font-size: 40px;">{winner}</h1>
                    <h2 style="font-size: 30px;">({count}표) 당선을 축하합니다!</h2>
                </div>
                """, unsafe_allow_html=True)
            if st.button("초기화"):
                st.session_state.votes = []
                st.session_state.show_winner = False
                st.rerun()

# ---------------------------------------------------------
# [학생 모드]
# ---------------------------------------------------------
else:
    info = st.session_state.election_info
    if st.session_state.has_voted:
        st.success("✅ 투표가 완료되었습니다! 잠시 기다려주세요.")
    else:
        st.title(f"{info['year']}학년도 {info['grade']}학년 {info['class']}반 회장 선거")
        if not st.session_state.candidates:
            st.warning("아직 후보자가 등록되지 않았습니다.")
        else:
            selection = st.radio("후보자를 선택하세요", 
                                 [f"기호 {c['symbol']}번 {c['name']}" for c in st.session_state.candidates])
            if st.button("제출하기"):
                st.session_state.votes.append(selection)
                st.session_state.has_voted = True
                st.rerun()