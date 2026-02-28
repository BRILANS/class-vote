import streamlit as st
import pandas as pd
import time
import random
import json
import os
from collections import Counter

# --- 설정 ---
st.set_page_config(page_title="학급회장 선거", layout="centered", initial_sidebar_state="collapsed")
DATA_FILE = "election_data.json"

# --- 데이터 읽기/쓰기 함수 ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"candidates": [], "votes": [], "info": {"year": 2026, "semester": 1, "grade": 1, "class": 1, "target": 25}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# --- 상태 초기화 ---
data = load_data()
if 'is_teacher_mode' not in st.session_state: st.session_state.is_teacher_mode = False

# --- URL 모드 ---
query_params = st.query_params
if query_params.get("mode") == "teacher" and not st.session_state.is_teacher_mode:
    password = st.sidebar.text_input("교사 비밀번호", type="password")
    if password == "1234":
        st.session_state.is_teacher_mode = True
        st.rerun()
    elif password != "": st.error("비밀번호 틀림")
    st.stop()

# ---------------------------------------------------------
# [교사 모드]
# ---------------------------------------------------------
if st.session_state.is_teacher_mode:
    st.title("👨‍🏫 선거 관리자 모드")
    
    # 수정할 때마다 데이터 불러오기
    data = load_data() 
    
    with st.expander("후보 관리 및 설정"):
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("후보 이름")
            if st.form_submit_button("후보 추가"):
                data["candidates"].append({"symbol": len(data["candidates"]) + 1, "name": name})
                save_data(data)
                st.rerun()
        if st.button("데이터 초기화"):
            save_data({"candidates": [], "votes": [], "info": data["info"]})
            st.rerun()
    
    st.write(f"현재 투표수: {len(data['votes'])}명")
    if st.button("🔥 개표 시작"):
        # (개표 로직은 동일)
        st.success("개표가 완료되었습니다!")

# ---------------------------------------------------------
# [학생 모드]
# ---------------------------------------------------------
else:
    st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)
    
    # 학생은 항상 최신 데이터를 파일에서 불러옴
    data = load_data()
    
    st.title(f"🗳️ {data['info']['grade']}학년 {data['info']['class']}반 회장 선거")
    
    # 세션별 투표 여부 확인
    if 'voted' in st.session_state:
        st.success("✅ 투표가 완료되었습니다.")
    elif not data["candidates"]:
        st.warning("아직 투표가 시작되지 않았습니다.")
    else:
        selection = st.radio("후보자를 선택하세요", [c['name'] for c in data["candidates"]])
        if st.button("제출하기"):
            data["votes"].append(selection)
            save_data(data) # 파일에 투표 저장
            st.session_state.voted = True
            st.rerun()