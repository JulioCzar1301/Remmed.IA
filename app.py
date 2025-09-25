from flask import Flask, request, jsonify, send_file
from Utils.query_router import QueryRouter
import sqlite3
import io

app = Flask(__name__)
router = QueryRouter(use_llm=True)


def get_db():
    conn = sqlite3.connect("./Sqlite/hospital_v2.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# @app.route("/exames", methods=["POST"])
# def inserir_exame():
#     data = request.form
#     id_paciente = data.get("id_paciente")
#     id_medico = data.get("id_medico")
#     tipo_exame = data.get("tipo_exame")
#     data_exame = data.get("data_exame")
#     resultado = data.get("resultado")
#     arquivo = request.files.get("arquivo")
#     arquivo_blob = arquivo.read() if arquivo else None

#     if not all([id_paciente, id_medico, tipo_exame, data_exame]):
#         return jsonify({"error": "Campos obrigatórios: id_paciente, id_medico, tipo_exame, data_exame"}), 400

#     conn = get_db()
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS exames (
#             id_exame INTEGER PRIMARY KEY AUTOINCREMENT,
#             id_paciente INTEGER NOT NULL,
#             id_medico INTEGER NOT NULL,
#             tipo_exame TEXT NOT NULL,
#             data_exame DATETIME NOT NULL,
#             resultado TEXT,
#             arquivo BLOB,
#             FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente),
#             FOREIGN KEY (id_medico) REFERENCES medicos(id_medico)
#         )
#     """)
#     cursor.execute(
#         """
#         INSERT INTO exames (id_paciente, id_medico, tipo_exame, data_exame, resultado, arquivo)
#         VALUES (?, ?, ?, ?, ?, ?)
#         """,
#         (id_paciente, id_medico, tipo_exame, data_exame, resultado, arquivo_blob)
#     )
#     conn.commit()
#     conn.close()
#     return jsonify({"message": "Exame inserido com sucesso."})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    id = data.get("id", "")
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Missing 'question' in request body."}), 400
    router.get_name_user()
    answer = router.execute(question)
    return jsonify({"question": question, "answer": answer})

@app.route("/create_patient", methods=["POST"])
def create_patient():
    data = request.get_json()
    name = data.get("name", "")
    cpf = data.get("cpf", "")
    birth_date = data.get("data_de_nascimento", "")
    peso = data.get("peso", "")
    sexo = data.get("sexo", "")
    altura = data.get("altura", "")
    alergias = data.get("alergias", "")
    historico_medico = data.get("historico_medico", "")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO pacientes (nome, cpf, data_nascimento, peso, sexo, altura, alergias, historico_medico) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (name, cpf, birth_date, peso, sexo, altura, alergias, historico_medico))
    conn.commit()
    conn.close()
    return jsonify({"message": "Paciente criado com sucesso."})

@app.route("/internacoes", methods=["POST"])
def get_internacoes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM internacoes")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    results = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return jsonify(results)

@app.route("/exames/<int:id_exame>/pdf", methods=["GET"])
def baixar_pdf(id_exame):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT arquivo FROM exames WHERE id_exame = ?", (id_exame,))
    row = cursor.fetchone()
    conn.close()
    if not row or not row[0]:
        return "Arquivo não encontrado", 404
    return send_file(io.BytesIO(row[0]), mimetype="application/pdf", as_attachment=True, download_name=f"exame_{id_exame}.pdf")

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
