import streamlit as st
import pandas as pd
import json
import os
from collections import Counter

# --- 1. 데이터 처리 함수 ---
def get_file_path(class_id): return f"data_{class_id}.json"

def load_data(class_id):
    path = get_file_path(class_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # 초기 데이터 구조
    return {"candidates": [], "votes": [], "info": {"school": "OO중학교", "year": 2026, "semester": 1, "grade": 1, "class": 1, "type": "학급회장", "target": 25}}

def save_data(class_id, data):
    with open(get_file_path(class_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# --- 2. 페이지 설정 ---
st.set_page_config(page_title="학급회장 선거", layout="centered", initial_sidebar_state="collapsed")

# --- 3. URL 모드 & 관리자 인증 ---
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
            st.session_state.school = st.text_input("학교 이름", value=data["info"].get("school", "OO중학교"))
            st.session_state.type = st.text_input("선거 구분 (예: 학급회장)", value=data["info"].get("type", "학급회장"))
            col1, col2 = st.columns(2)
            st.session_state.grade = col1.number_input("학년", value=data["info"].get("grade", 1))
            st.session_state.class_num = col2.number_input("반", value=data["info"].get("class", 1))
            st.session_state.target = st.number_input("목표 투표 인원", value=data["info"].get("target", 25))
            
            if st.button("정보 저장"):
                data["info"].update({"school": st.session_state.school, "type": st.session_state.type, 
                                     "grade": st.session_state.grade, "class": st.session_state.class_num, "target": st.session_state.target})
                save_data(class_id, data); st.success("저장 완료!")

        with tab2:
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("후보 이름")
                if st.form_submit_button("후보 추가"):
                    data["candidates"].append({"name": name})
                    save_data(class_id, data); st.rerun()
            
            if data["candidates"]:
                df = pd.DataFrame(data["candidates"])
                st.dataframe(df, use_container_width=True)
                # 삭제 기능
                del_name = st.selectbox("삭제할 후보 선택", [c['name'] for c in data["candidates"]])
                if st.button("선택한 후보 삭제"):
                    data["candidates"] = [c for c in data["candidates"] if c['name'] != del_name]
                    save_data(class_id, data); st.rerun()

        with tab3:
            st.info(f"현재 투표수: {len(data['votes'])} / {data['info']['target']}")
            if st.button("🔄 투표 초기화"): data["votes"] = []; save_data(class_id, data); st.rerun()
            if st.button("🔥 개표 시작"): st.success("개표 로직 실행 중...")

# ---------------------------------------------------------
# [학생 모드]
# ---------------------------------------------------------
else:
    st.markdown("<style>#MainMenu {visibility: hidden;}</style>", unsafe_allow_html=True)
    class_id = st.text_input("학급 ID 입력")
    if class_id:
        data = load_data(class_id)
        # 동적 헤더 출력
        info = data["info"]
        st.title(f"🗳️ {info['school']} {info['grade']}학년 {info['class']}반 {info['type']} 선거")
        
        if 'has_voted' not in st.session_state: st.session_state.has_voted = False
        if st.session_state.has_voted: st.success("✅ 투표가 완료되었습니다!")
        elif not data["candidates"]: st.warning("아직 후보자가 없습니다.")
        else:
            selection = st.radio("후보자를 선택하세요", [c["name"] for c in data["candidates"]])
            if st.button("제출하기"):
                data["votes"].append(selection)
                save_data(class_id, data)
                st.session_state.has_voted = True; st.rerun()