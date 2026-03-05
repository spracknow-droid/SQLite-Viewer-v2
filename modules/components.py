import streamlit as st

def render_stats(tables, views):
    c1, c2 = st.columns(2)
    c1.metric("📦 물리 테이블", f"{len(tables)}개")
    c2.metric("✨ 가상 뷰(View)", f"{len(views)}개")

def render_query_editor():
    st.sidebar.subheader("⌨️ SQL 실행기")
    query = st.sidebar.text_area("SQL 문 입력 (CREATE VIEW...)", height=250)
    btn = st.sidebar.button("실행하기", use_container_width=True)
    return query, btn

def render_data_browser(tables, views):
    st.write("### 📊 데이터 브라우저")
    c1, c2 = st.columns([1, 2])
    with c1:
        target_type = st.radio("종류", ["Table", "View"], horizontal=True)
    with c2:
        options = tables if target_type == "Table" else views
        selected = st.selectbox(f"{target_type} 선택", options)
    return target_type, selected
