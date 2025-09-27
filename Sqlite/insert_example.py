import sqlite3
from datetime import datetime

def insert_db():
    """Popula todas as tabelas com dados de exemplo."""
    try:
        conn = sqlite3.connect("hospital.db")
        cursor = conn.cursor()

        # -------------------- Pacientes --------------------
        pacientes = [
            ("Ana Souza", "12345678901", "1990-05-12", 65.0, "F", 1.68, "Dipirona", "Hipertensão"),
            ("Carlos Pereira", "23456789012", "1985-09-23", 82.5, "M", 1.75, "Nenhuma", "Asma"),
            ("João Silva", "34567890123", "2000-02-01", 70.3, "M", 1.80, "Glúten", "Histórico de enxaqueca"),
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO pacientes (nome, cpf, data_nascimento, peso, sexo, altura, alergias, historico_medico)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, pacientes)

        # -------------------- Médicos --------------------
        medicos = [
            ("Dr. Mariana Lima", "CRM12345"),
            ("Dr. Paulo Mendes", "CRM54321"),
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO medicos (nome, crm)
            VALUES (?, ?)
        """, medicos)

        # -------------------- Consultas --------------------
        consultas = [
            (1, 1, "2025-01-10 10:00:00", "Dor de cabeça", "Enxaqueca"),
            (2, 2, "2025-02-15 14:30:00", "Tosse persistente", "Bronquite"),
            (3, 1, "2025-03-20 09:00:00", "Check-up anual", "Saudável"),
        ]
        cursor.executemany("""
            INSERT INTO consultas (id_paciente, id_medico, data_consulta, motivo, diagnostico)
            VALUES (?, ?, ?, ?, ?)
        """, consultas)

        # -------------------- Internações --------------------
        internacoes = [
            (1, "2025-01-05", "2025-01-12", "Cirurgia de apendicite", 1, "Recuperação estável"),
            (2, "2025-02-20", None, "Pneumonia", 2, "Paciente em observação"),
            (3, "2025-03-25", "2025-04-02", "Fratura no braço", 1, "Paciente liberado com gesso"),
        ]
        cursor.executemany("""
            INSERT INTO internacoes (id_paciente, data_entrada, data_saida, motivo, id_medico, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, internacoes)

        # -------------------- Exames --------------------
        exames = [
            (1, 1, "Hemograma", "2025-01-08 09:00:00", "Todos os valores dentro do normal"),
            (2, 2, "Raio-X Torácico", "2025-02-21 11:00:00", "Sinais de bronquite"),
            (3, 1, "Ultrassom Abdominal", "2025-03-26 14:00:00", "Sem alterações relevantes"),
        ]
        cursor.executemany("""
            INSERT INTO exames (id_paciente, id_medico, tipo_exame, data_exame, resultado)
            VALUES (?, ?, ?, ?, ?)
        """, exames)

        conn.commit()
        print("Banco de dados hospital_v2.db criado e populado com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao criar/popular banco: {e}")
    finally:
        if conn:
            conn.close()

insert_db()
