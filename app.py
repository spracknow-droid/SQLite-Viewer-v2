import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="SQLite Viewer Fix", layout="wide")

# 1. 세션 상태 초기화 (DB 연결 유지용)
if 'db_path' not in st.session_state:
    st.session_state.db_path = None

st.title("🛡️ SQLite View Creator (Fix)")

# 2. 파일 업로드 및 저장
uploaded_file = st.sidebar.file_uploader("DB 파일 업로드", type=["db", "sqlite"])

if uploaded_file:
    # 파일을 한 번만 저장
    if st.session_state.db_path is None:
        temp_name = "database_fix.db"
        with open(temp_name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.db_path = temp_name

    # DB 연결
    conn = sqlite3.connect(st.session_state.db_path, check_same_thread=False)
    
    # --- 사이드바: 쿼리 입력 ---
    st.sidebar.subheader("✨ VIEW 생성기")
    st.sidebar.info("예시: CREATE VIEW my_view AS SELECT * FROM 테이블명")
    sql_input = st.sidebar.text_area("SQL 문 입력", height=200)
    
    if st.sidebar.button("명령 실행"):
        try:
            # 특수 공백 제거 및 실행
            clean_sql = sql_input.replace('\xa0', ' ').strip()
            conn.executescript(clean_sql)
            conn.commit()
            st.sidebar.success("✅ 실행 성공! 아래에서 'View'를 선택하세요.")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"❌ 실패: {e}")

    # --- 메인 화면: 데이터 조회 ---
    # 현재 DB에 있는 모든 테이블과 뷰를 새로고침해서 가져옴
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist()
    views = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='view';", conn)['name'].tolist()

    st.write("### 📊 DB 내부 현황")
    col1, col2 = st.columns(2)
    col1.write(f"**테이블 목록:** {', '.join(tables)}")
    col2.write(f"**뷰(View) 목록:** {', '.join(views)}")

    st.divider()

    # 데이터 브라우저
    target_type = st.radio("종류 선택", ["Table", "View"], horizontal=True)
    target_list = tables if target_type == "Table" else views
    
    selected = st.selectbox(f"{target_type} 선택", target_list)

    if selected:
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{selected}" LIMIT 100', conn)
            st.write(f"📂 **{selected}** 데이터 (최대 100행)")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"불러오기 실패: {e}")

    conn.close()
else:
    st.info("사이드바에서 DB 파일을 먼저 올려주세요.")
