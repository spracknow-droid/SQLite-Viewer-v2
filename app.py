import streamlit as st
import pandas as pd
import sqlite3
import io

st.set_page_config(page_title="Excel to SQLite Converter", layout="wide")

st.title("📊 Excel to SQLite 변환기")
st.markdown("엑셀 파일을 업로드하고 컬럼 타입을 지정하여 SQLite DB로 저장하세요.")

# 1. 사이드바 - 파일 업로드
st.sidebar.header("1. 파일 업로드")
uploaded_file = st.sidebar.file_uploader("엑셀 파일을 선택하세요", type=["xlsx", "xls"])

if uploaded_file:
    # 데이터 읽기 (미리보기용)
    df = pd.read_excel(uploaded_file)
    st.subheader("📋 데이터 미리보기")
    st.dataframe(df.head(10))

    st.divider()

    # 2. 테이블 및 컬럼 설정
    st.subheader("⚙️ DB 테이블 설정")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        table_name = st.text_input("테이블 이름 입력", value="my_table")
    
    st.write("각 컬럼의 데이터 타입을 지정하세요:")
    
    # 컬럼 타입 선택을 위한 딕셔너리
    type_options = {"문자열 (TEXT)": "TEXT", "정수 (INTEGER)": "INTEGER", "실수 (REAL)": "REAL"}
    selected_types = {}
    
    # 컬럼 설정 영역을 그리드로 배치
    cols = st.columns(4)
    for i, col_name in enumerate(df.columns):
        with cols[i % 4]:
            selected_types[col_name] = st.selectbox(
                f"컬럼: {col_name}",
                options=list(type_options.keys()),
                key=f"col_{col_name}"
            )

    # 3. DB 생성 및 저장 로직
    if st.button("🚀 SQLite DB 생성하기"):
        try:
            # 인메모리가 아닌 임시 바이트 객체에 저장하기 위해 io 사용
            output = io.BytesIO()
            
            # 실제 DB 생성 및 데이터 삽입
            # 가상 연결을 생성하여 스키마를 정의합니다.
            conn = sqlite3.connect(":memory:") # 우선 메모리에서 작업
            cursor = conn.cursor()
            
            # SQL Create Table 문 생성
            cols_with_types = ", ".join([f'"{c}" {type_options[selected_types[c]]}' for c in df.columns])
            create_table_sql = f'CREATE TABLE "{table_name}" ({cols_with_types})'
            
            cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')
            cursor.execute(create_table_sql)
            
            # 데이터 삽입
            df.to_sql(table_name, conn, if_exists='append', index=False)
            
            # 생성된 DB를 파일로 내보내기 위해 임시 파일 생성
            # (Streamlit Cloud 환경 등을 고려하여 메모리 내 복사 방식 사용)
            temp_db = io.BytesIO()
            new_db_conn = sqlite3.connect("temp.db")
            conn.backup(new_db_conn)
            new_db_conn.close()
            
            with open("temp.db", "rb") as f:
                db_byte_data = f.read()

            st.success(f"✅ '{table_name}' 테이블이 포함된 DB 파일이 준비되었습니다!")

            # 4. 다운로드 버튼
            st.download_button(
                label="💾 SQLite DB 다운로드",
                data=db_byte_data,
                file_name=f"{table_name}.db",
                mime="application/x-sqlite3"
            )
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

else:
    st.info("왼쪽 사이드바에서 엑셀 파일을 먼저 업로드해주세요.")
