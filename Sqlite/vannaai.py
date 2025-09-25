from vanna.chromadb import ChromaDB_VectorStore
import os
from vanna.google import GoogleGeminiChat
from vanna.base import VannaBase
from groq import Groq


class MyCustomLLM(VannaBase):
    def __init__(self, config=None):
        if config is None:
            raise ValueError(
                "For Groq, config must be provided with an api_key and model"
            )

        if "api_key" not in config:
            raise ValueError("config must contain a Groq api_key")

        if "model" not in config:
            raise ValueError("config must contain a Groq model")

        api_key = config["api_key"]
        model = config["model"]
        self.client = Groq(api_key=api_key)
        self.model = model
    def system_message(self, message: str) -> any:
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> any:
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> any:
        return {"role": "assistant", "content": message}

    def generate_sql(self, question: str, **kwargs) -> str:
        sql = super().generate_sql(question, **kwargs)

        sql = sql.replace("\\_", "_")

        return sql
    
    def submit_prompt(self, prompt, **kwargs) -> str:
        # Ex: [{"role": "user", "content": "..."}]
        chat_response = self.client.chat.completions.create(
            model=self.model,
            messages=prompt,  
        )

        return chat_response.choices[0].message.content
    
class MyVanna(ChromaDB_VectorStore, MyCustomLLM):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        MyCustomLLM.__init__(self, config=config)

# Configuração (igual ao estilo Mistral)
config = {
    "api_key": os.getenv("GROQ_API_KEY"),   # ⚠️ Substitua!
    "model": "llama-3.3-70b-versatile",                 # ou "mixtral-8x7b-32768", etc.
    "path": "vanna_chromadb_db"                    # opcional, para persistência local
}

vn = MyVanna(config=config)

vn.connect_to_sqlite('hospital_v2.db')

df_ddl = vn.run_sql("SELECT type, sql FROM sqlite_master WHERE sql is not null")

for ddl in df_ddl['sql'].to_list():
  vn.train(ddl=ddl)

training_data = vn.get_training_data()
print(training_data)