# routes/query_router.py
import os
from groq import Groq
from .rag_medicines import search_pinecone
from .vanna_sql import create_vanna_instance
import json
import re
import sqlite3

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def chat_with_groq(prompt, model="llama-3.3-70b-versatile"):
    answer = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
        temperature=0.2
    )

    return answer.choices[0].message.content


class QueryRouter:
    def __init__(self, use_llm=False, llama_model="llama-3.3-70b-versatile"):
        self.vn = create_vanna_instance()
        self.use_llm = use_llm
        self.llama_model = llama_model
        self.name_user = ""
        
    def get_name_user(self):
        conn = sqlite3.connect("./Sqlite/hospital_v2.db")
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM medicos WHERE id_medico = 1")
        result = cursor.fetchone()
        conn.close()
        print("Fetched name:", result)
        self.name_user = result[0] if result else "Usuário"
    
    def classify_by_keywords(self, question: str) -> str:
        question_lower = question.lower()
        terms_leaflets = [
            "drug", "medicine", "dose", "effect", "side effect", "allergy", "pain",
            "remédio", "bula", "medicamento", "efeito colateral", "alergia", "dor",
            "indicado", "trata", "contra-indicação", "composição"
        ]
        terms_sql = [
            "patient", "doctor", "appointment", "admission", "hospital", "registration",
            "paciente", "médico", "consulta", "internação", "cadastro", "exame",
            "diagnóstico", "receita", "prescrição", "medicação", "medicamento prescrito"
        ]

        found_leaflets = any(t in question_lower for t in terms_leaflets)
        found_sql = any(t in question_lower for t in terms_sql)

        if found_leaflets and found_sql:
            return "ambos"
        elif found_leaflets:
            return "bulas"
        elif found_sql:
            return "sql"
        return "bulas"  # fallback

    def classify_with_llm(self, question: str) -> str:
        instruction = f"""Você é um classificador de intenções. 
Classifique a pergunta do usuário em APENAS uma destas opções, respondendo somente com a palavra: 'bulas', 'sql' ou 'ambos'. Ao classificar,
verifique se a pergunta envolve informações sobre medicamentos/bulas, dados de pacientes/exames, ou ambos. Seja conciso e direto.
Pergunta: {question}
Resposta:
"""
        response = chat_with_groq(instruction, model="meta-llama/llama-4-maverick-17b-128e-instruct").strip().lower()
        print("LLM classification:", response)
        if "ambos" in response or "both" in response:
            return "ambos"
        elif "sql" in response:
            return "sql"
        return "bulas"

    def execute(self, question: str) -> str:
        if self.use_llm:
            route = self.classify_with_llm(question)
        else:
            route = self.classify_by_keywords(question)

        print("Chosen route:", route)

        if route == "bulas":
            return self.enhanced_rag_query(question)

        elif route == "sql":
            return self._execute_sql_query(question)

        elif route == "ambos":
            return self._handle_combined_query(question)

        else:
            return "Não foi possível classificar a consulta."

    def _execute_sql_query(self, question: str):
        sql, df, chart = self.vn.ask(question, allow_llm_to_see_data=True)
        print("Debug:\n", sql)

        if df.empty:
            intermediate_answer = "Nenhum resultado encontrado."
        else:
            intermediate_answer = df.to_string(index=False)

        # checar se consulta envolve binário
        if ("exames" in sql.lower() and "arquivo" in sql.lower()) or "arquivo" in df.columns:
            print("✅ O SQL busca a coluna 'arquivo' na tabela 'exame'")

            # pega o id_exame do df (assumindo que vem junto na query)
            if "id_exame" in df.columns:
                id_exame = df.iloc[0]["id_exame"]
                return {"pdf": True, "id_exame": id_exame}
            else:
                return {"pdf": True, "id_exame": None}
        else:
            print("❌ O SQL NÃO busca 'arquivo' em 'exame'")
            print(df)

            prompt = f"""
            Pergunta do usuário com nome {self.name_user}, informe o nome dele na resposta: {question}
            Resultados da consulta SQL: {intermediate_answer}
            Escreva uma resposta clara, natural e educada em português para o usuário, sem mencionar SQL, tabelas ou estruturas técnicas
            """
            return {"pdf": False, "resposta": chat_with_groq(prompt)}


    def enhanced_rag_query(self, question: str) -> str:
        """
        Busca contexto relevante usando Pinecone e retorna resposta natural via Llama3.
        """
        results = search_pinecone(question, top_k=2)
        
        hits = results.get('result', {}).get('hits', [])
        
        context_text = []
        for i, res in enumerate(hits):
            fields = res.get('fields', {})
            chunk_text = fields.get('chunk_text', '')
            context_text.append(chunk_text)
            
        context = "\n\n".join([res for res in context_text])
        prompt = f"""
        Pergunta do usuário com nome {self.name_user},informe o nome dele na resposta: {question}
        Informações encontradas na bula.
        {context}
        Escreva uma resposta clara, natural e educada em português para o usuário, sem mencionar processos técnicos ou estrutura dos documentos.
        """
    
        return chat_with_groq(prompt)

    def _handle_combined_query(self, question: str) -> str:
        # Passo 1: Perguntar ao LLM se há dependência entre as partes
        dependency_check_prompt = f"""
        A pergunta a seguir envolve tanto informações sobre medicamentos quanto dados de pacientes ou exames:

        "{question}"

        Responda apenas com "sim" se a parte sobre medicamentos DEPENDE dos resultados da consulta ao banco de dados (ex: saber qual medicamento o paciente X está tomando).
        Responda apenas com "não" se as duas partes podem ser respondidas independentemente.

        Exemplo 1: "Quais são os efeitos colaterais da medicação que o paciente João está tomando?" → sim
        Exemplo 2: "Quem é o cardiologista de Maria e qual remédio posso tomar para dor de cabeça?" → não

        Resposta ("sim" ou "não"):
        """

        depends_response = chat_with_groq(dependency_check_prompt, model="meta-llama/llama-4-maverick-17b-128e-instruct").strip().lower()
        has_dependency = "sim" in depends_response

        if has_dependency:
            print("→ Dependência detectada: SQL primeiro, depois RAG")
            # Etapa 1: Extrair a parte SQL
            extract_sql_prompt = f"""
            Extraia APENAS a parte da pergunta que se refere a dados de pacientes, médicos, exames ou hospitalares.
            Pergunta original: "{question}"
            Retorne apenas a pergunta SQL, nada mais.
            """
            sql_question = chat_with_groq(extract_sql_prompt).strip()
            print("Extracted SQL question:", sql_question)
            # Etapa 2: Executar SQL
            self._execute_sql_query(sql_question)
            sql, df, chart = self.vn.ask(sql_question, allow_llm_to_see_data=True)
            

            # Etapa 3: Extrair informação relevante (ex: nome do medicamento)
            # Vamos pedir ao LLM para extrair o dado útil para a próxima etapa
            extract_info_prompt = f"""
            Com base nos resultados abaixo, extraia APENAS o nome do medicamento, substância, sintoma de doença, ou tratamento mencionado.
            Se houver mais de um, liste-os separados por vírgulas.

            Resultados:
            {df.to_string(index=False)}

            Resposta (apenas os nomes, sem explicações):
            """
            extracted_info = chat_with_groq(extract_info_prompt, model="meta-llama/llama-4-maverick-17b-128e-instruct").strip()
            print("Extracted info for leaflet query:", extracted_info)
            # Etapa 4: Formular pergunta para o RAG usando a informação extraída


            leaflet_answer = self.enhanced_rag_query(extracted_info)
            print("Leaflet answer:", leaflet_answer)
            # Etapa 5: Resumir tudo com o LLM
            final_prompt = f"""
            O usuário com nome {self.name_user},informe o nome dele na resposta, perguntou: "{question}"

            Primeiro, obtivemos do banco de dados:
            {df.to_string(index=False)}

            Depois, buscamos na bula do medicamento '{extracted_info}' e encontramos:
            {leaflet_answer}

            Elabore uma resposta única, clara e natural em português, conectando os dois resultados, sem mencionar processos técnicos.
            """

            return chat_with_groq(final_prompt)

        else:
            print("→ Sem dependência: executando consultas separadamente")
            # Separar perguntas com LLM
            split_prompt = f"""
            Separe a pergunta abaixo em DUAS partes independentes:

            1. Uma parte sobre medicamentos/bulas.
            2. Outra parte sobre pacientes/exames/banco de dados.

            Pergunta: "{question}"

            Retorne no formato JSON:
            {{
                "medicine_question": "pergunta sobre medicamento",
                "sql_question": "pergunta sobre banco de dados"
            }}
            """

            split_response = chat_with_groq(split_prompt)
            text = split_response.content if hasattr(split_response, "content") else str(split_response)

            # Extrair JSON
            match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                json_text = match.group(1)
                try:
                    split_dict = json.loads(json_text)
                except json.JSONDecodeError:
                    split_dict = {"medicine_question": question, "sql_question": question}
            else:
                split_dict = {"medicine_question": question, "sql_question": question}

            med_q = split_dict.get("medicine_question", question)
            sql_q = split_dict.get("sql_question", question)

            # Executar ambas
            leaflet_answer = self.enhanced_rag_query(med_q)
            sql_answer = self._execute_sql_query(sql_q)
            # Combine as respostas usando Llama3
            prompt = f"""
            O usuário com nome {self.name_user},informe o nome dele na resposta, perguntou: {question}
            Informações do medicamento:
            {leaflet_answer}
            Dados do paciente/sistema:
            {sql_answer}
            Elabore uma resposta única, clara e natural em português, conectando os dois resultados, sem mencionar processos técnicos.
            """
            
            return chat_with_groq(prompt)