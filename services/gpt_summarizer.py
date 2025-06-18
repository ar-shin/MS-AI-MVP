import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from services.prompt_loader import load_prompt_template

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
)

DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
TEMPLATE_PATH = "prompts/rfp_prompt01.txt"


def summarize_text(text):
    prompt_template = load_prompt_template(TEMPLATE_PATH)
    final_prompt = prompt_template.format(text=text)

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {
                "role": "system",
                "content": "당신은 SI 프로젝트 수주 제안서를 검토하는 전문가입니다. RFP 문서를 읽고, 요구사항 분석 및 리스크 식별을 명확하게 수행합니다.",
            },
            {
                "role": "user",
                "content": final_prompt,
            },
        ],
        # temperature=0.4, dev-o4-mini 모델은 temperature 파라미터를 지원하지 않음
    )
    return response.choices[0].message.content

def select_representative_summary(summaries, embedding_model):
    vectors = [get_embedding(s, model) for s in summaries]
    center = np.mean(vectors, axis=0)
    distances = [np.linalg.norm(np.array(v) - center) for v in vectors]
    best_idx = np.argmin(distances)
    return summaries[best_idx]
