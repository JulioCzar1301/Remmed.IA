import sqlite3
from datetime import date, datetime

def insert_db():
    """Popula todas as tabelas com dados de exemplo."""
    try:
        conn = sqlite3.connect("hospital_v2.db")
        cursor = conn.cursor()

         # Inserindo pacientes
        pacientes = [
            ("Ana Souza", "12345678901", "1990-05-12", 65.0, "F", 1.68, "Dipirona", "Hipertensão"),
            ("Carlos Pereira", "23456789012", "1985-09-23", 82.5, "M", 1.75, "Nenhuma", "Asma"),
            ("João Silva", "34567890123", "2000-02-01", 70.3, "M", 1.80, "Glúten", "Histórico de enxaqueca"),
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO pacientes (nome, cpf, data_nascimento, peso, sexo, altura, alergias, historico_medico)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, pacientes)

        # Inserindo médicos
        medicos = ("Dr. Mariana Lima", "CRM12345")
        
        cursor.execute("""
            INSERT OR IGNORE INTO medicos (nome, crm)
            VALUES (?, ?)
        """, medicos)

        # Inserindo consultas
        consultas = [
            (1, 1, "2025-01-10 10:00:00", "Dor de cabeça", "Enxaqueca"),
            (2, 2, "2025-02-15 14:30:00", "Tosse persistente", "Bronquite"),
            (3, 1, "2025-03-20 09:00:00", "Check-up anual", "Saudável"),
        ]
        cursor.executemany("""
            INSERT INTO consultas (id_paciente, id_medico, data_consulta, motivo, diagnostico)
            VALUES (?, ?, ?, ?, ?)
        """, consultas)


        conn.commit()
        print("Banco de dados hospital_v2.db criado e populado com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao criar/popular banco: {e}")
    finally:
        if conn:
            conn.close()

insert_db()