import streamlit as st
import pandas as pd
import time
import random
import json
import os
from collections import Counter

# --- 1. 파일 경로 설정 함수 ---
def get_file_path(class_id):
    return f"data_{class_id}.json"

def load_data(class_id):
    path = get_file_path(class_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # 데이터가 없으면 기본 구조 생성
    return {"candidates": [], "votes": [], "info": {"year": 2026, "target": 25}}

def save_data(class_id, data):
    with open(get_file_path(class_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# --- 2. 기본 설정 ---
st.set_page_config(page_title="학급회장 선거", layout="centered", initial_sidebar_state="collapsed")

# --- 3. 관리자/학생 모드 구분 ---
query_params = st.query_params
is_teacher = query_params.get("mode") == "teacher"

# ---------------------------------------------------------
# [교사 모드]
# ---------------------------------------------------------
if is_teacher:
    st.title("👨‍🏫 선거 관리자 모드")
    
    # 학급 선택 (데이터 격리의 핵심)
    class_id = st.text_input("학급 ID를 입력하세요 (예: 1-1)", key="admin_class")
    
    if class_id:
        data = load_data(class_id)
        
        # 롤백: 이전 버전의 탭 UI
        tab1, tab2, tab3 = st.tabs(["1. 정보 설정", "2. 후보 관리", "3. 개표 대시보드"])

        with tab1:
            st.session_state.target = st.number_input("투표 목표 인원", value=data["info"]["target"])
            if st.button("저장"):
                data["info"]["target"] = st.session_state.target
                save_data(class_id, data)

        with tab2:
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("후보 이름")
                if st.form_submit_button("후보 추가"):
                    data["candidates"].append({"symbol": len(data["candidates"]) + 1, "name": name})
                    save_data(class_id, data)
                    st.rerun()
            
            if data["candidates"]:
                df = pd.DataFrame(data["candidates"])
                st.dataframe(df, use_container_width=True)
                if st.button("후보 초기화"):
                    data["candidates"] = []
                    save_data(class_id, data); st.rerun()

        with tab3:
            st.info(f"현재 투표수: {len(data['votes'])} / {data['info']['target']}")
            if st.button("🔥 개표 시작"):
                # (개표 애니메이션 로직...)
                st.success("개표가 완료되었습니다!")

# ---------------------------------------------------------
# [학생 모드]
# ---------------------------------------------------------
else:
    st.markdown("<style>#MainMenu {visibility: hidden;}</style>", unsafe_allow_html=True)
    
    st.title("🗳️ 학급회장 선거")
    class_id = st.text_input("학급 ID를 입력하세요 (선생님이 알려주신 번호)")
    
    if class_id:
        data = load_data(class_id)
        if not data["candidates"]:
            st.warning("아직 후보자가 등록되지 않았거나 학급 ID가 잘못되었습니다.")
        else:
            selection = st.radio("후보자를 선택하세요", [c["name"] for c in data["candidates"]])
            if st.button("제출하기"):
                data["votes"].append(selection)
                save_data(class_id, data)
                st.success("투표 완료!")