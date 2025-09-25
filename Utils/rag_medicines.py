import os
from pinecone import Pinecone

def search_pinecone(query_text, top_k=5, fields=None, namespace="bulas-namespace"):
    """
    Realiza busca no Pinecone e retorna os resultados.
    :param query_text: Texto para busca
    :param top_k: Número de resultados
    :param fields: Lista de campos/metadados a retornar
    :param namespace: Namespace do Pinecone
    :return: Lista de resultados
    """
    if fields is None:
        fields = ["remedio", "arquivo", "chunk_text"]
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(host="https://bula-medicas-py-pla8ace.svc.aped-4627-b74a.pinecone.io")
    results = index.search(
        namespace=namespace,
        query={
            "inputs": {"text": query_text},
            "top_k": top_k
        },
        fields=fields
    )
    return results
