from flask import Flask, request, jsonify, send_file
from Utils.query_router import QueryRouter
import sqlite3
import io
import json
import datetime
from flask_cors import CORS  

app = Flask(__name__)
router = QueryRouter(use_llm=True)
CORS(app)

def get_db():
    conn = sqlite3.connect("./Sqlite/hospital.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    token = data.get("token", "")
    question = data.get("question", "")
    if not question:
        return jsonify({"error": "Missing 'question' in request body."}), 400
    if token not in ["doctor","reception"]:
        return jsonify({"error": "Token is invalid."}), 400
    if token == "doctor":
        router.get_name_user()

    answer = router.execute(question, token)
    return jsonify({"question": question, "answer": answer})


@app.route("/create_exam", methods=["POST"])
def inserir_exame():
    data = request.form
    id_paciente = data.get("id_paciente")
    id_medico = data.get("id_medico")
    tipo_exame = data.get("tipo_exame")
    data_exame = data.get("data_exame")
    resultado = data.get("resultado")

    if not all([id_paciente, id_medico, tipo_exame, data_exame]):
        return jsonify({"error": "Campos obrigatórios: id_paciente, id_medico, tipo_exame, data_exame"}), 400

    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO exames (id_paciente, id_medico, tipo_exame, data_exame, resultado)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (id_paciente, id_medico, tipo_exame, data_exame, resultado)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Exame inserido com sucesso."})

@app.route("/exam/<int:id_exame>/", methods=["GET"])
def obter_exame(id_exame):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT arquivo FROM exames WHERE id_exame = ?", (id_exame,))
    row = cursor.fetchone()
    conn.close()
    if not row or not row[0]:
        return "Arquivo não encontrado", 404
    return send_file(io.BytesIO(row[0]), mimetype="application/pdf", as_attachment=True, download_name=f"exame_{id_exame}.pdf")


@app.route("/create_pacient", methods=["POST"])
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
    temperatura = data.get("temperatura", "")
    oxigenacao = data.get("oxigenacao", "")
    frequencia_cardiaca = data.get("frequencia_cardiaca", "")   
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO pacientes (nome, cpf, data_nascimento, peso, sexo, altura, alergias, historico_medico, temperatura, oxigenacao, frequencia_cardiaca) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (name, cpf, birth_date, peso, sexo, altura, alergias, historico_medico))
    conn.commit()
    conn.close()
    return jsonify({"message": "Paciente criado com sucesso."})

@app.route("/get_pacients", methods=["GET"])
def get_pacients():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id_paciente, nome FROM pacientes")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return json.dumps(rows)

@app.route("/get_pacient/<int:id_paciente>", methods=['GET'])
def get_pacient(id_paciente):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE id_paciente = ?", (id_paciente,))
    row = dict(cursor.fetchone())
    conn.close()
    return json.dumps(row)


@app.route("/create_appointment", methods=["POST"])
def create_appointment():
    data = request.get_json()
    id_paciente = data.get("id_paciente")
    id_medico = data.get("id_medico")
    data_consulta = data.get("data_consulta", datetime.now().isoformat())
    motivo = data.get("motivo")
    diagnostico = data.get("diagnostico")

    if not all([id_paciente, id_medico]):
        return jsonify({"erro": "Campos obrigatórios: id_paciente e id_medico"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO consultas (id_paciente, id_medico, data_consulta, motivo, diagnostico)
        VALUES (?, ?, ?, ?, ?)
        """,
        (id_paciente, id_medico, data_consulta, motivo, diagnostico),
    )
    conn.commit()
    consulta_id = cursor.lastrowid
    conn.close()

    return jsonify({"mensagem": "Consulta criada com sucesso", "id_consulta": consulta_id}), 201

@app.route("/get_appointment/<int:id_paciente>", methods=['GET'])
def get_appointment(id_paciente):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM consultas WHERE id_paciente=?",(id_paciente,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return json.dumps(rows)

@app.route("/create_hospitalization", methods=["POST"])
def create_hospitalization():
    data = request.get_json()
    id_paciente = data.get("id_paciente")
    data_entrada = data.get("data_entrada", datetime.now().date().isoformat())
    data_saida = data.get("data_saida")  # opcional
    motivo = data.get("motivo")
    id_medico = data.get("id_medico")
    observacoes = data.get("observacoes")

    if not all([id_paciente, motivo]):
        return jsonify({"erro": "Campos obrigatórios: id_paciente e motivo"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO internacoes (id_paciente, data_entrada, data_saida, motivo, id_medico, observacoes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (id_paciente, data_entrada, data_saida, motivo, id_medico, observacoes),
    )
    conn.commit()
    internacao_id = cursor.lastrowid
    conn.close()

    return jsonify({"mensagem": "Internação criada com sucesso", "id_internacao": internacao_id}), 201

@app.route("/get_hospitalization/<int:id_paciente>", methods=["GET"])
def get_hospitalization(id_paciente):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM internacoes WHERE id_paciente=?",(id_paciente,))
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    results = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return jsonify(results)


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)



    
