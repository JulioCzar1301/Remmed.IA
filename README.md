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

project/
│── app.py # Arquivo principal Flask
│── requirements.txt # Dependências
│── Utils/
│ ├── query_router.py # Rotas de consultas
│ ├── rag_medicines.py # Funções de RAG com Pinecone
│ └── vanna_sql.py # Integração com Vanna
│── Sqlite/
│ └── hospital_v2.db # Banco SQLite (exemplo)
│── VetorDatabase/
│ └── create_databse_pinecone # População do Banco Vetorial
│── WebScraping/
│ └── medicamentos #armazena todo texto coletado
| └── medicamentos_v2 #retira redundâncias dos textos coletados
| └── link_medicamentos #link de cada bula buscada e processada
│ └── spyder.py #Faz a raspagem dos dados do site de consulta de medicos
│── README.md # Documentação

```
git clone https://github.com/JulioCzar1301/Remmed.IA.git
cd seu-repo
```