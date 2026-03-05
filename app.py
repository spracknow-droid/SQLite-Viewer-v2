import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Advanced SQLite Manager", layout="wide")

# DB 연결 및 메타데이터 가져오기 함수
def get_objects(cursor, obj_type):
    # type='table' 또는 type='view' 선택
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='{obj_type}';")
    return [row[0] for row in cursor.fetchall()]

st.title("🗂️ SQLite Table & View Manager")

uploaded_file = st.sidebar.file_uploader("SQLite 파일 업로드", type=["db", "sqlite"])

if uploaded_file:
    # 임시 파일 저장
    temp_db = "managed_user_db.db"
    with open(temp_db, "wb") as f:
        f.write(uploaded_file.getbuffer())

    conn = sqlite3.connect(temp_db, check_same_thread=False)
    
    # --- 1. VIEW 생성 섹션 ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("✨ 새로운 VIEW 만들기")
    view_name = st.sidebar.text_input("VIEW 이름", placeholder="v_user_summary")
    view_query = st.sidebar.text_area("SQL Query (SELECT문)", placeholder="SELECT * FROM table WHERE...")
    
    if st.sidebar.button("VIEW 생성"):
        if view_name and view_query:
            try:
                conn.execute(f"CREATE VIEW {view_name} AS {view_query}")
                st.sidebar.success(f"'{view_name}' 뷰가 생성되었습니다!")
                st.rerun() # 화면 새로고침하여 목록 갱신
            except Exception as e:
                st.sidebar.error(f"실패: {e}")
        else:
            st.sidebar.warning("이름과 쿼리를 모두 입력하세요.")

    # --- 2. 데이터 조회 섹션 ---
    tabs = st.tabs(["📊 데이터 조회", "🛠️ VIEW 관리"])

    with tabs[0]:
        obj_type = st.radio("오브젝트 타입", ["Table", "View"], horizontal=True)
        objects = get_objects(conn.cursor(), obj_type.lower())
        
        selected_obj = st.selectbox(f"{obj_type} 선택", objects)
        
        if selected_obj:
            df = pd.read_sql_query(f"SELECT * FROM {selected_obj}", conn)
            st.dataframe(df, use_container_width=True)

    with tabs[1]:
        st.subheader("🗑️ VIEW 삭제")
        all_views = get_objects(conn.cursor(), 'view')
        if all_views:
            target_view = st.selectbox("삭제할 VIEW 선택", all_views)
            if st.button("선택한 VIEW 삭제", type="primary"):
                conn.execute(f"DROP VIEW {target_view}")
                st.success(f"'{target_view}' 삭제 완료")
                st.rerun()
        else:
            st.write("생성된 VIEW가 없습니다.")

    # 다운로드 버튼 (수정된 DB 저장)
    with open(temp_db, "rb") as f:
        st.sidebar.download_button("수정된 DB 다운로드", f, file_name="updated_database.db")

    conn.close()
