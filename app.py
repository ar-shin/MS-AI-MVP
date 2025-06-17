import streamlit as st
from services.document_intelligence import extract_text_from_file
from services.gpt_summarizer import summarize_text
from services.chunker import chunk_text
from services.fp_classifier import classify_fp_coefficients
from services.similar_project_search import search_similar_projects

st.title("AI 기반 RFP 분석 및 리스크 평가 AGENT")

uploaded_file = st.file_uploader("📄 RFP 파일 업로드", type=["pdf", "docx"])

if uploaded_file and "chunks" not in st.session_state:
    with st.spinner("⏳ 문서 분석 중..."):
        text = extract_text_from_file(uploaded_file)
        chunks = chunk_text(text)
        results = [summarize_text(chunk) for chunk in chunks]

        st.session_state["text"] = text
        st.session_state["chunks"] = chunks
        st.session_state["summaries"] = results

if "summaries" in st.session_state:
    for i, res in enumerate(st.session_state["summaries"], 1):
        st.subheader(f"📌 요약 {i}")
        st.write(res)

    with st.spinner("🔎 유사 프로젝트 검색 중..."):
        query_summary = "\n".join(st.session_state["summaries"])
        similar_projects = search_similar_projects(
            query_text=query_summary,
            embedding_model="text-embedding-3-small",  # 혹은 배포한 모델 이름
        )

        st.subheader("🧩 참고용 유사 프로젝트 추천")
        for idx, project in enumerate(similar_projects, 1):
            st.markdown(f"**{idx}. {project['title']}**  \n" f"- {project['chunk']}")

    if st.button("AI 기반 SW개발비 산정(FP방식)"):
        with st.spinner("🤖 보정계수 판단 중..."):
            from services.fp_classifier import classify_fp_coefficients
            import json

            # 1. 전체 텍스트 기반 판단
            full_text = "\n\n".join(st.session_state["chunks"])
            coefficient_json = classify_fp_coefficients(full_text)

            st.markdown("### 📊 AI 판단 보정계수 결과")
            st.json(coefficient_json)

            # 2. 계수 테이블 로딩
            with open("data/fp_coefficients.json", "r", encoding="utf-8") as f:
                fp_table = json.load(f)

            # 3. 계수 매칭 및 계산
            total = 0
            # count = 0
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
