import streamlit as st
import json
from services.document_intelligence import extract_text_from_file
from services.gpt_summarizer import summarize_text
from services.gpt_summarizer import select_representative_summary
from services.chunker import chunk_text
from services.chat_def import classify_fp_coefficients
from services.similar_project_search import search_similar_projects
from services.utils import init_session_state
from services.chat_def import answer_question

# 세션 초기화
init_session_state()

# UI 구성
st.set_page_config(page_title="AI 기반 RFP 분석 Agent", layout="wide")

st.markdown(
    """
    <h1 style='text-align: center; color: #003366; font-size: 2.5em;'>🤖 AI 기반 RFP 분석 Agent</h1>
    <p style='text-align: center; color: gray;'>LLM 기반 요약, 유사 프로젝트 추천, 문서 기반 질문봇, SW개발비 산정까지 한번에!</p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

uploaded_file = st.file_uploader("📄 RFP 문서를 업로드해주세요", type=["pdf", "ppt"], key="file_upload")
prev_file = st.session_state.get("uploaded_filename")

# 파일 삭제 체크
if uploaded_file is None and prev_file:
    # st.session_state["tab_option"] = "📄 요약"
    init_session_state(force_reset=True)
    st.rerun()

# 파일 변경 체크
elif uploaded_file and uploaded_file.name != prev_file:
    # st.session_state["tab_option"] = "📄 요약"
    init_session_state(force_reset=True)
    st.session_state["uploaded_filename"] = uploaded_file.name
    st.rerun()


st.markdown("""
<style>
div[data-testid="stRadio"] {
    display: flex;
    justify-content: center;
    align-items: center;
}

div[role="radiogroup"] > label {
    border: 1px solid #d3d3d3;
    border-radius: 8px;
    padding: 0.5em 1.2em;
    margin-right: 0.5em;
    margin-bottom: 0.3em;
    background-color: #f7f9fc;
    color: #003366;
    font-weight: 500;
    transition: 0.2s ease-in-out;
    cursor: pointer;
    box-shadow: 0 0 3px rgba(0,0,0,0.05);
}
div[role="radiogroup"] > label:hover {
    background-color: #e6f0ff;
}
div[role="radiogroup"] > label[data-selected="true"] {
    background-color: #003366;
    color: white;
    font-weight: bold;
    border-color: #003366;
}
div[data-testid="stRadio"] > label {
    display: none;
}
</style>
""", unsafe_allow_html=True)

TAB_LABELS = ["📄 요약", "💬 질문하기", "💲SW개발비 산정"]
tab_option = st.radio(
    label="", 
    options=TAB_LABELS, 
    horizontal=True,
    index=TAB_LABELS.index(st.session_state.get("tab_option", "📄 요약")),
    key="tab_option_radio"
)

if tab_option != st.session_state["tab_option"]:
    st.session_state["tab_option"] = tab_option
    st.rerun()

st.markdown("---")


if tab_option == "📄 요약":
    if uploaded_file is None:
        st.markdown("📢 RFP 문서를 업로드하면 AI가 내용을 요약하고 유사 프로젝트를 추천해드립니다.")

    if uploaded_file and st.session_state["chunks"] is None:
        with st.spinner("⏳ 문서 분석 중..."):
            text = extract_text_from_file(uploaded_file)
            chunks = chunk_text(text)
            results = [summarize_text(chunk) for chunk in chunks]

            best_summary = select_representative_summary(
                results,
                embedding_model="dev-text-embedding-3-small"
            )

            st.session_state["text"] = text
            st.session_state["chunks"] = chunks
            st.session_state["summaries"] = best_summary

    if "summaries" in st.session_state and st.session_state["summaries"] is not None:
        st.subheader(f"📌 요약")
        st.write(st.session_state["summaries"])

        with st.spinner("🔎 유사 프로젝트 검색 중..."):
            query_summary = st.session_state["summaries"]
            similar_projects = search_similar_projects(
                query_text=query_summary,
                embedding_model="dev-text-embedding-3-small",
            )

            st.markdown("---")
            st.subheader("🧩 참고용 유사 프로젝트 추천")
            for idx, project in enumerate(similar_projects, 1):
                st.markdown(f"**{idx}. {project['title']}**  \n" f"- {project['chunk']}")

elif tab_option == "💬 질문하기":
    if uploaded_file is None:
        st.markdown("📢 RFP 문서를 업로드하면 AI가 내용을 분석하여 질문에 답변해드립니다.")

    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_question = st.chat_input("질문을 입력하세요")

    if user_question:
        st.session_state.messages.append({"role": "user", "content": user_question})

        with st.chat_message("assistant"):
            with st.spinner("🤖 답변 생성 중..."):
                context = "\n".join(st.session_state["chunks"])

                answer = answer_question(context, user_question)

                st.markdown(answer)

                st.session_state.messages.append({"role": "assistant", "content": answer})
    

elif tab_option == "💲SW개발비 산정":
    if uploaded_file is None:
        st.markdown("📢 RFP 문서를 업로드하면 AI가 내용을 분석하여 보정계수를 판단하고, SW개발비를 산정해드립니다.")

    if st.session_state["chunks"] is not None:
        with st.spinner("🤖 보정계수 판단 중..."):
            # 1. 전체 텍스트 기반 판단
            full_text = "\n\n".join(st.session_state["chunks"])
            coefficient_json = classify_fp_coefficients(full_text)

            st.markdown("### 📊 AI 판단 보정계수 결과")
            st.json(coefficient_json)

            # 2. 계수 테이블 로딩
            with open("data/fp_coefficients.json", "r", encoding="utf-8") as f:
                fp_table = json.load(f)

            # 3. 계수 매칭 및 계산
            total = 1
            breakdown = []

            for category, selected_value in coefficient_json.items():
                category_table = fp_table.get(category, {})
                factor = category_table.get(selected_value)
                if factor:
                    breakdown.append(
                        f"🔹 **{category}**: {selected_value} → 계수 {factor}"
                    )
                    total *= factor
                    # count += 1
                else:
                    breakdown.append(
                        f"⚠️ **{category}**: '{selected_value}'에 대한 계수를 찾을 수 없습니다."
                    )

            # 4. 출력
            st.markdown("### ✅ 계산 결과 요약")
            for line in breakdown:
                st.markdown(line)

            if total > 0:
                # avg = round(total / count, 3)
                st.success(f"💡 최종 보정계수: **{total}**")
            else:
                st.error(
                    "❌ 계산 가능한 계수가 없습니다. 프롬프트 또는 입력값을 확인해주세요."
                )

            # st.markdown("### 🔧 사용자 선택 보정계수로 총 개발비용 계산")
            # user_selection = {}
            # for category, options in fp_table.items():
            #     gpt_default = coefficient_json.get(category, "애매함")
            #     selected = st.selectbox(
            #         f"{category}",
            #         options=list(options.keys()) + ["애매함"],
            #         index=(
            #             (list(options.keys()) + ["애매함"]).index(gpt_default)
            #             if gpt_default in options
            #             else len(options)
            #         ),
            #     )
            #     user_selection[category] = selected
