# 🧪 REMM.IA – Exames e Consultas

Esta aplicação é uma **API em Flask** que permite o **upload, armazenamento e consulta de arquivos PDF de exames médicos**.  
Além disso, a API integra-se com **Groq**, **Pinecone** e **Vanna** para oferecer suporte a **busca semântica** e **consultas inteligentes em linguagem natural**.

---

## 🚀 Funcionalidades

- Upload de exames em PDF via plataforma web  
- Armazenamento dos arquivos no banco **SQLite** (formato binário)  
- Download dos exames armazenados  
- Integração com **Pinecone** para busca semântica de dados médicos  
- Integração com **Groq** para processamento de linguagem natural  
- Uso do **Vanna + ChromaDB** para análise de consultas em SQL  

---

## 📦 Tecnologias Utilizadas

- [Flask](https://flask.palletsprojects.com/)  
- [SQLite](https://www.sqlite.org/)  
- [Groq](https://groq.com/)  
- [Pinecone](https://www.pinecone.io/)  
- [Vanna](https://vanna.ai/)  
- [ChromaDB](https://www.trychroma.com/)  
- [python-dotenv](https://pypi.org/project/python-dotenv/)  

---

## 📂 Estrutura do Projeto

project/ <br>
├── app.py                     # Arquivo principal Flask<br>
├── requirements.txt           # Dependências<br>
├── Utils/<br>
│   ├── query_router.py      # Rotas de consultas<br>
│   ├── rag_medicines.py     # Funções de RAG com Pinecone<br>
│   └── vanna_sql.py         # Integração com Vanna<br>
├── Sqlite/<br>
│   └── hospital_v2.db       # Banco SQLite (exemplo)<br>
├── VetorDatabase/<br>
│   └── create_databse_pinecone  # População do Banco Vetorial<br>
├── WebScraping/<br>
│   ├── medicamentos           # Armazena todo texto coletado<br>
│   ├── medicamentos_v2        # Retira redundâncias dos textos coletados<br>
│   ├── link_medicamentos      # Link de cada bula buscada e processada<br>
│   └── spyder.py              # Faz a raspagem dos dados do site de consulta de medicos<br>
└── README.md                  # Documentação

## Etapas
### Etapa 1: Clonar Repositório
```
git clone https://github.com/JulioCzar1301/Remmed.IA.git
cd seu-repo
```

### Etapa 2: Instalar Dependências
No terminal
```
pip install -r requirements.txt
```

### Etapa 3: Adicionar as chaves de API(Groq e Pinecone)
No seu terminal window:
```
$env:GROQ_API_KEY="sua chave do groq"
$env:PINECONE_API_KEY="minha chave do pinecone"
```

### Etapa 4: Rodar API

```
python app.py
```

