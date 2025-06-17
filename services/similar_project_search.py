import os
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential

load_dotenv()

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY")),
)
openai_client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
)


def search_similar_projects(query_text, embedding_model, k=5):
    embedding_response = openai_client.embeddings.create(
        input=query_text, model=embedding_model
    )

    embedding_vector = embedding_response.data[0].embedding

    # results = search_client.search(
    #     vector=embedding_vector,
    #     k=k,
    #     vector_fields="text_vector",
    # )

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

    # results = list(search_results)
    # print(results)

    return [{"title": doc.get("prjName"), "chunk": doc.get("chunk")} for doc in search_results]
