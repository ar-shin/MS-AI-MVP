import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from services.utils import load_prompt_template
import re
import json

load_dotenv()

# 환경 변수 설정
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
)

DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
TEMPLATE_PATH_1 = "prompts/rfp_fp_prompt01.txt"
TEMPLATE_PATH_2 = "prompts/rfp_chat_prompt01.txt"


def clean_key(key: str) -> str:
    # 줄바꿈, 양쪽 공백, 따옴표, 이상한 문장부호 제거
    return re.sub(r"[^ㄱ-힣a-zA-Z0-9가-힣\s]", "", key).strip()


def clean_value(value: str) -> str:
    return value.strip().replace("\n", "")

def extract_json_from_text(text: str) -> dict:
    # ```json 블럭 제거
    cleaned = re.sub(r"```json|```", "", text).strip()

    # JSON 부분 추출
    json_match = re.search(r"\{[\s\S]*\}", cleaned)
    if json_match:
        json_str = json_match.group()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"[JSON 파싱 오류] {e}\n\n원본:\n{json_str}")
    else:
        raise ValueError(f"[JSON 미포함 응답]\n\n{cleaned}")

def classify_fp_coefficients(text):
    prompt_template = load_prompt_template(TEMPLATE_PATH_1)
    final_prompt = prompt_template.format(text=text)

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {
                "role": "system",
                "content": "당신은 RFP를 분석하여 SW 개발비 산정을 위한 보정계수 판단을 수행하는 전문가입니다.",
            },
            {
                "role": "user",
                "content": final_prompt,
            },
        ],
        # temperature=0,  # 정확도 중요
    )

    content = response.choices[0].message.content.strip()

    # JSON 파싱 시도
    try:
        result = extract_json_from_text(content)

        cleaned_result = {
            clean_key(key): clean_value(value) for key, value in result.items()
        }

        return cleaned_result
    except json.JSONDecodeError:
        raise ValueError(f"GPT 응답이 JSON 형식이 아님:\n\n{content}")


def answer_question(context, question):
    prompt_template = load_prompt_template(TEMPLATE_PATH_2)
    final_prompt = prompt_template.format(context=context, question=question)

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {
                "role": "system", 
                "content": "당신은 SI RFP 분석 전문가입니다. 문서를 기반으로 정확하게 답변해주세요."
            },
            {
                "role": "user", 
                "content": final_prompt
            },
        ],
    )

    return response.choices[0].message.content.strip()