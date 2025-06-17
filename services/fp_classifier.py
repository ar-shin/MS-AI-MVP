import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from services.prompt_loader import load_prompt_template
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
TEMPLATE_PATH = "prompts/rfp_fp_prompt01.txt"


def clean_key(key: str) -> str:
    # 줄바꿈, 양쪽 공백, 따옴표, 이상한 문장부호 제거
    return re.sub(r"[^ㄱ-힣a-zA-Z0-9가-힣\s]", "", key).strip()


def clean_value(value: str) -> str:
    return value.strip().replace("\n", "")


def classify_fp_coefficients(text):
    prompt_template = load_prompt_template(TEMPLATE_PATH)
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
        result = json.loads(content)

        cleaned_result = {
            clean_key(key): clean_value(value) for key, value in result.items()
        }

        return cleaned_result
    except json.JSONDecodeError:
        raise ValueError(f"GPT 응답이 JSON 형식이 아님:\n\n{content}")
