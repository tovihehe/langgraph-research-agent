from sqlalchemy import create_engine, text
import os
import time
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class PostgreConnector:
    def __init__(self):
        self.db_uri = self._get_db_uri()
        self.engine = create_engine(self.db_uri)
        self.connector_type = 'postgres'

    def _get_db_uri(self):
        """Returns the database URI based on environment variables."""
        PGHOST = os.getenv('PGHOST')
        PGDATABASE = os.getenv('PGDATABASE')
        PGUSER = os.getenv('PGUSER')
        PGPASSWORD = os.getenv('PGPASSWORD')
        return f"postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}/{PGDATABASE}"

    def get_connection_string(self):
        return self.db_uri

    def execute_query(self, query):
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return result.fetchall()

    def fetch_table_columns(self, table_name):
        query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_name}';
        """
        return self.execute_query(query)

    def fetch_table_primary_key(self, table_name):
        query = f"""
        SELECT kcu.column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'PRIMARY KEY';
        """
        return self.execute_query(query)

    def fetch_table_foreign_keys(self, table_name):
        query = f"""
        SELECT
            kcu.column_name,
            ccu.table_name AS referenced_table,
            ccu.column_name AS referenced_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
        WHERE tc.table_name = '{table_name}' AND tc.constraint_type = 'FOREIGN KEY';
        """
        return self.execute_query(query)

    def fetch_and_save_schema_with_relations(self, output_file="db_schema.json"):
        """Extracts the database schema, including PK and FK, and saves it to a JSON file."""
        pk_query = text("""
        SELECT
            tc.table_name,
            kcu.column_name
        FROM
            information_schema.table_constraints AS tc
        JOIN
            information_schema.key_column_usage AS kcu
        ON
            tc.constraint_name = kcu.constraint_name
        AND
            tc.table_schema = kcu.table_schema
        WHERE
            tc.constraint_type = 'PRIMARY KEY'
        AND
            tc.table_schema = 'public';
        """)

        fk_query = text("""
        SELECT
            tc.table_name AS fk_table,
            kcu.column_name AS fk_column,
            ccu.table_name AS referenced_table,
            ccu.column_name AS referenced_column
        FROM
            information_schema.table_constraints AS tc
        JOIN
            information_schema.key_column_usage AS kcu
        ON
            tc.constraint_name = kcu.constraint_name
        AND
            tc.table_schema = kcu.table_schema
        JOIN
            information_schema.constraint_column_usage AS ccu
        ON
            ccu.constraint_name = tc.constraint_name
        AND
            ccu.table_schema = tc.table_schema
        WHERE
            tc.constraint_type = 'FOREIGN KEY'
        AND
            tc.table_schema = 'public';
        """)

        try:
            with self.engine.connect() as conn:
                columns_result = conn.execute(text("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
                """)).fetchall()

                pk_result = conn.execute(pk_query).fetchall()
                fk_result = conn.execute(fk_query).fetchall()
        except Exception as e:
            print(f"Error al conectar o ejecutar consultas: {e}")
            return

        schema = {}
        for table, column, dtype in columns_result:
            schema.setdefault(table, {"columns": [], "primary_key": [], "foreign_keys": []})
            schema[table]["columns"].append({"column_name": column, "data_type": dtype})

        for table, column in pk_result:
            schema[table]["primary_key"].append(column)

        for fk_table, fk_column, ref_table, ref_column in fk_result:
            schema[fk_table]["foreign_keys"].append({
                "fk_column": fk_column,
                "referenced_table": ref_table,
                "referenced_column": ref_column
            })

        try:
            with open(output_file, "w") as f:
                json.dump(schema, f, indent=4)
        except IOError as e:
            print(f"Error writing to file {output_file}: {e}")

    @staticmethod
    def load_schema_from_file(schema_file="db_schema.json"):
        """Carga el esquema desde un archivo JSON."""
        with open(schema_file, "r") as f:
            schema = json.load(f)
        return schema

    def get_schema(self, schema_file="db_schema.json", update_interval=86400):
        """
        Devuelve el esquema desde un archivo JSON, actualizándolo si ha expirado el intervalo.
        
        Args:
            schema_file (str): Ruta al archivo donde se guarda el esquema.
            update_interval (int): Tiempo en segundos después del cual el esquema se actualiza. Default: 1 día.

        Returns:
            dict: Esquema de la base de datos.
        """
        if not os.path.exists(schema_file) or (time.time() - os.path.getmtime(schema_file)) > update_interval:
            print("Actualizando esquema de la base de datos...")
            self.fetch_and_save_schema_with_relations(schema_file)
        else:
            print("Esquema cargado desde el archivo.")
        
        return self.load_schema_from_file(schema_file)


if __name__ == "__main__":
    connector = PostgreConnector()
    output_file = "db_schema.json"
    print("Generando esquema de la base de datos...")
    connector.fetch_and_save_schema_with_relations(output_file)
    print(f"Esquema guardado en {output_file}")