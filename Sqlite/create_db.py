import sqlite3

def create_db():
    """
    Cria e configura o banco de dados do hospital, removendo a tabela de prontuários.
    """
    try:
        conn = sqlite3.connect("hospital.db")
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
            historico_medico TEXT,
            temperatura REAL,
            oxigenacao INTEGER,
            frequencia_cardiaca INTEGER
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exames (
            id_exame INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER NOT NULL,
            id_medico INTEGER NOT NULL,
            tipo_exame TEXT NOT NULL,
            data_exame DATETIME NOT NULL,
            resultado TEXT,
            FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente),
            FOREIGN KEY (id_medico) REFERENCES medicos(id_medico)
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

        conn.execute('''
            CREATE TABLE internacoes (
            id_internacao   INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente     INTEGER NOT NULL,
            data_entrada    DATE NOT NULL,
            data_saida      DATE,
            motivo          TEXT NOT NULL,
            id_medico       INTEGER,
            observacoes     TEXT,
            FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente),
            FOREIGN KEY (id_medico) REFERENCES medicos(id_medico)
                                                                );
        ''')

        


        conn.commit()
        print("Banco de dados hospital_v2.db criado com sucesso, sem a tabela de prontuários!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao criar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

create_db()
