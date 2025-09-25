import sqlite3

def create_db():
    """
    Cria e configura o banco de dados do hospital, removendo a tabela de prontuários.
    """
    try:
        conn = sqlite3.connect("hospital_v2.db")
        cursor = conn.cursor()

        # Tabela de pacientes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            data_nascimento DATE NOT NULL,
            peso REAL,
            sexo TEXT CHECK(sexo IN ('M','F','Outro')),
            altura REAL,
            alergias TEXT,
            historico_medico TEXT
        )
        """)

        # Tabela de médicos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicos (
            id_medico INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            crm TEXT UNIQUE NOT NULL
        )
        """)

        # Tabela de consultas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultas (
            id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER NOT NULL,
            id_medico INTEGER NOT NULL,
            data_consulta DATETIME NOT NULL,
            motivo TEXT,
            diagnostico TEXT,
            FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente),
            FOREIGN KEY (id_medico) REFERENCES medicos(id_medico)
        )
        """)

        conn.commit()
        print("Banco de dados hospital_v2.db criado com sucesso, sem a tabela de prontuários!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao criar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

create_db()
