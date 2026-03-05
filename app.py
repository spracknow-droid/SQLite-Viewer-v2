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

    # 데이터베이스 연결 (커밋 자동 반영을 위해 isolation_level 설정)
    conn = sqlite3.connect(temp_db, check_same_thread=False)
    
    # --- 1. SQL 실행 섹션 (VIEW 생성 등) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("✨ SQL 실행 (VIEW 생성)")
    # 사용자가 작성한 CREATE VIEW 문장을 그대로 받기 위해 text_area를 크게 설정
    custom_query = st.sidebar.text_area(
        "SQL 쿼리 입력", 
        placeholder="CREATE VIEW 뷰이름 AS SELECT ...",
        height=300
    )
    
    if st.sidebar.button("SQL 실행"):
        if custom_query:
            try:
                # \xa0 같은 특수 공백 제거 및 실행
                clean_query = custom_query.replace('\xa0', ' ').strip()
                conn.executescript(clean_query)
                conn.commit()
                st.sidebar.success("성공적으로 실행되었습니다!")
                st.rerun() 
            except Exception as e:
                st.sidebar.error(f"실패: {e}")
        else:
            st.sidebar.warning("쿼리를 입력하세요.")

    # --- 2. 데이터 조회 및 관리 섹션 ---
    tabs = st.tabs(["📊 데이터 조회", "🛠️ VIEW 관리"])

    with tabs[0]:
        col1, col2 = st.columns([1, 3])
        with col1:
            obj_type = st.radio("오브젝트 타입", ["Table", "View"], horizontal=True)
        
        objects = get_objects(conn.cursor(), obj_type.lower())
        
        with col2:
            selected_obj = st.selectbox(f"{obj_type} 선택", objects)
        
        if selected_obj:
            try:
                df = pd.read_sql_query(f"SELECT * FROM \"{selected_obj}\"", conn)
                st.write(f"#### [{obj_type}] {selected_obj} ({len(df)} rows)")
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.error(f"데이터를 불러오는 중 오류 발생: {e}")

    with tabs[1]:
        st.subheader("🗑️ VIEW 삭제")
        all_views = get_objects(conn.cursor(), 'view')
        if all_views:
            target_view = st.selectbox("삭제할 VIEW 선택", all_views)
            if st.button("선택한 VIEW 삭제", type="primary"):
                try:
                    conn.execute(f"DROP VIEW \"{target_view}\"")
                    conn.commit()
                    st.success(f"'{target_view}' 삭제 완료")
                    st.rerun()
                except Exception as e:
                    st.error(f"삭제 실패: {e}")
        else:
            st.write("생 성된 VIEW가 없습니다.")

    # 다운로드 버튼 (수정된 DB 저장)
    st.sidebar.markdown("---")
    with open(temp_db, "rb") as f:
        st.sidebar.download_button("💾 수정된 DB 다운로드", f, file_name="updated_database.db")

    conn.close()
