# routes/vanna_sql.py
import os
from dotenv import load_dotenv
from vanna.chromadb import ChromaDB_VectorStore
from vanna.base import VannaBase
from groq import Groq

load_dotenv()

class CustomLLM(VannaBase):
    def __init__(self, config=None):
        if config is None or "api_key" not in config or "model" not in config:
            raise ValueError("Config must contain api_key and model")
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
        return sql.replace("\\_", "_")

    def submit_prompt(self, prompt, **kwargs) -> str:
        chat_response = self.client.chat.completions.create(
            model=self.model,
            messages=prompt,
        )
        return chat_response.choices[0].message.content


class MyVanna(ChromaDB_VectorStore, CustomLLM):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        CustomLLM.__init__(self, config=config)


def create_vanna_instance():
    config = {
        "api_key": os.getenv("GROQ_API_KEY"),
        "model": "llama-3.3-70b-versatile",
        "path": 'Sqlite/vanna_chromadb_db'
    }
    vn = MyVanna(config=config)
    vn.connect_to_sqlite('./Sqlite/hospital.db')
    return vn