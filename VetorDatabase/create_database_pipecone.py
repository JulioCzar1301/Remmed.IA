from pinecone import Pinecone
import os
import glob
from sentence_transformers import SentenceTransformer
import time
import random

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
# Corrigido: remova espaços extras no host!
host = "https://bula-medicas-py-pla8ace.svc.aped-4627-b74a.pinecone.io"
index = pc.Index(host=host)

base_dir = "./../WebScraping/medicamentos_v2"
arquivos_txt = glob.glob(os.path.join(base_dir, "**", "*.txt"), recursive=True)

records = []
MAX_METADATA_SIZE = 40960  # 40 KB em bytes
MAX_NOME_SIZE = 100  # aumentado um pouco; ajuste conforme necessário

def get_utf8_size(s: str) -> int:
    return len(s.encode('utf-8'))

def split_chunk_if_needed(chunk_text: str, remedio: str, max_meta_size: int) -> list[str]:
    """
    Divide chunk_text em partes menores se (chunk_text + remedio) exceder max_meta_size.
    Retorna uma lista de subchunks que respeitam o limite.
    """
    remedio_size = get_utf8_size(remedio)
    # Reserva ~100 bytes para estrutura JSON e outros campos (como "_id" no backend)
    available_for_text = max_meta_size - remedio_size - 100
    if available_for_text <= 0:
        # Nome muito grande — truncar remedio
        remedio = remedio.encode('utf-8')[:max_meta_size - 200].decode('utf-8', errors='ignore')
        available_for_text = 200  # mínimo razoável

    if get_utf8_size(chunk_text) <= available_for_text:
        return [chunk_text]

    # Dividir o chunk em partes menores
    words = chunk_text.split()
    subchunks = []
    current = []

    for word in words:
        test_chunk = ' '.join(current + [word])
        if get_utf8_size(test_chunk) <= available_for_text:
            current.append(word)
        else:
            if current:
                subchunks.append(' '.join(current))
                current = [word]
            else:
                # Palavra única maior que o limite — força inclusão
                subchunks.append(word)
                current = []

    if current:
        subchunks.append(' '.join(current))

    return subchunks

cont = 1
for arq in arquivos_txt:
    nome = os.path.splitext(os.path.basename(arq))[0]
    # Trunca nome se necessário
    if get_utf8_size(nome) > MAX_NOME_SIZE:
        nome = nome.encode('utf-8')[:MAX_NOME_SIZE].decode('utf-8', errors='ignore')

    with open(arq, 'r', encoding='utf-8', errors='ignore') as f:
        conteudo = f.read().strip()
    if not conteudo:
        continue

    chunks = [c.strip() for c in conteudo.split("\n\n") if c.strip()]
    chunk_counter = 0

    for i, chunk in enumerate(chunks):
        subchunks = split_chunk_if_needed(chunk, nome, MAX_METADATA_SIZE)
        for sub_i, subchunk in enumerate(subchunks):
            record = {
                "_id": f"{nome}_{i}_{sub_i}",  # inclui sub_i para unicidade
                "chunk_text": subchunk,
                "remedio": nome,
            }
            records.append(record)
            chunk_counter += 1

    print(f"Processado {cont} de {len(arquivos_txt)}, total subchunks: {chunk_counter}.")
    cont += 1

print(f"Total de registros para inserir: {len(records)}")

# Embaralhar após o índice 2161
random.seed(42)
if len(records) > 2161:
    records_to_shuffle = records[2161:]
    random.shuffle(records_to_shuffle)
    records = records[:2161] + records_to_shuffle

# Upsert em lote
batch_size = 90
start_index = 4503
for i in range(start_index, len(records), batch_size):
    batch = records[i:i + batch_size]
    index.upsert_records("bulas-namespace", batch)
    print(f"Upserted records {i} to {min(i + batch_size, len(records))}")
    time.sleep(3)  

print("Indexação concluída com sucesso!")