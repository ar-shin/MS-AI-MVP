import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

def extract_text_from_file(file):
    endpoint = os.getenv("AZURE_FORM_ENDPOINT")
    key = os.getenv("AZURE_FORM_KEY")
    client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    poller = client.begin_analyze_document("prebuilt-document", document=file)
    result = poller.result()
    full_text = "\n".join([line.content for page in result.pages for line in page.lines])
    return full_text
