import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from services.utils import get_embedding

load_dotenv()

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")),
)
# openai_client = AzureOpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),
#     api_version=os.getenv("OPENAI_API_VERSION"),
#     azure_endpoint=os.getenv("AZURE_ENDPOINT"),
# )


def search_similar_projects(query_text, embedding_model, k=5):
    embedding_vector = [get_embedding(s, model) for s in summaries]

    search_results = search_client.search(
        search_text="",
        vector_queries=[
            {
                "kind": "vector",
                "vector": embedding_vector,
                "fields": "text_vector",
                "k": k,
            }
        ],
    )

    return [{"title": doc.get("prjName"), "chunk": doc.get("chunk")} for doc in search_results]
