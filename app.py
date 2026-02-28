import streamlit as st
import pandas as pd
import json
import os

# --- 1. 파일 경로 및 데이터 처리 함수 ---
def get_file_path(class_id):
    return f"data_{class_id}.json"

def load_data(class_id):
    path = get_file_path(class_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"candidates": [], "votes": [], "info": {"target": 25}}

def save_data(class_id, data):
    with open(get_file_path(class_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# --- 2. 기본 설정 ---
st.set_page_config(page_title="학급회장 선거", layout="centered", initial_sidebar_state="collapsed")

# --- 3. 관리자/학생 모드 구분 ---
query_params = st.query_params
is_teacher = query_params.get("mode") == "teacher"

# 세션 상태 초기화 (학생용)
if 'has_voted' not in st.session_state: st.session_state.has_voted = False
if 'last_class_id' not in st.session_state: st.session_state.last_class_id = None

# ---------------------------------------------------------
# [교사 모드]
# ---------------------------------------------------------
if is_teacher:
    st.title("👨‍🏫 선거 관리자 모드")
    class_id = st.text_input("학급 ID를 입력하세요 (예: 1-1)")
    
    if class_id:
        data = load_data(class_id)
        tab1, tab2, tab3 = st.tabs(["1. 정보 설정", "2. 후보 관리", "3. 개표 대시보드"])

        with tab1:
            target = st.number_input("투표 목표 인원", value=data["info"]["target"])
            if st.button("저장"):
                data["info"]["target"] = target
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
                st.success("개표가 완료되었습니다!")

# ---------------------------------------------------------
# [학생 모드]
# ---------------------------------------------------------
else:
    st.markdown("<style>#MainMenu {visibility: hidden;}</style>", unsafe_allow_html=True)
    st.title("🗳️ 학급회장 선거")
    class_id = st.text_input("학급 ID를 입력하세요")
    
    if class_id:
        # 다른 반 ID로 바꾸면 투표 상태 초기화
        if st.session_state.last_class_id != class_id:
            st.session_state.has_voted = False
            st.session_state.last_class_id = class_id

        data = load_data(class_id)
        
        # 투표 완료 여부 확인
        if st.session_state.has_voted:
            st.success("✅ 투표가 완료되었습니다! 소중한 한 표 감사합니다.")
        elif not data["candidates"]:
            st.warning("아직 투표가 시작되지 않았습니다.")
        else:
            selection = st.radio("후보자를 선택하세요", [c["name"] for c in data["candidates"]])
            if st.button("제출하기"):
                data["votes"].append(selection)
                save_data(class_id, data)
                st.session_state.has_voted = True  # 투표 완료 표시!
                st.rerun()