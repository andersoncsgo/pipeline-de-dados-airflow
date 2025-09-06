import os
import pandas as pd
from datetime import datetime
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook


AIRFLOW_DATA_PATH = "/opt/airflow/data"
AIRFLOW_OUTPUT_PATH = "/opt/airflow/output"
POSTGRES_SOURCE_CONN_ID = "postgres_source"
POSTGRES_DW_CONN_ID = "postgres_dw"

TABLES_TO_EXTRACT = [
    "agencias",
    "clientes",
    "colaboradores",
    "contas",
    "propostas_credito",
]

# Definição da DAG #teste
@dag(
    dag_id="banvic_data_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="35 4 * * *",
    catchup=False,
    tags=["banvic", "data-engineering"],
    doc_md="""
    # Pipeline de Dados (BanVic)
    
    Esta dag realiza a extração diária de dados de duas fontes:
    1.  Um banco de dados PostgreSQL .
    2.  Um arquivo CSV contendo transações carregá-los em um Data Warehouse centralizado

    """
)
def banvic_pipeline():
    
    @task
    def create_daily_output_dirs(logical_date: datetime) -> str: #cria os diretórios de saída com a data da execução

        date_str = logical_date.strftime('%Y-%m-%d') 
        
        base_path = os.path.join(AIRFLOW_OUTPUT_PATH, date_str)
        csv_source_path = os.path.join(base_path, 'csv_source')
        sql_source_path = os.path.join(base_path, 'sql_source')
        
        os.makedirs(csv_source_path, exist_ok=True)
        os.makedirs(sql_source_path, exist_ok=True)
        
        return base_path

    @task
    def extract_from_csv(base_output_path: str) -> str:
        """Lê o arquivo transacoes.csv e o salva no diretório de saída."""
        source_file_path = os.path.join(AIRFLOW_DATA_PATH, 'transacoes.csv')
        output_file_path = os.path.join(base_output_path, 'csv_source', 'transacoes.csv')
        
        print(f"Lendo de {source_file_path}")
        df = pd.read_csv(source_file_path)
        
        print(f"Escrevendo para {output_file_path}")
        df.to_csv(output_file_path, index=False)
        
        return output_file_path

    @task
    def extract_from_postgres(base_output_path: str) -> str:
        """Extrai todas as tabelas do banco de dados fonte para arquivos CSV."""
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_SOURCE_CONN_ID)
        output_dir = os.path.join(base_output_path, 'sql_source')
        
        for table_name in TABLES_TO_EXTRACT:
            output_file_path = os.path.join(output_dir, f"{table_name}.csv")
            print(f"Extraindo tabela '{table_name}' para '{output_file_path}'...")
            
            sql_query = f"COPY {table_name} TO STDOUT WITH CSV HEADER"
            
            pg_hook.copy_expert(sql=sql_query, filename=output_file_path)
            
        return output_dir

    @task
    def load_to_data_warehouse(csv_output_path: str, sql_output_dir: str):#carrega os dados extraidos Data Lake para o data warehouse
        
        pg_dw_hook = PostgresHook(postgres_conn_id=POSTGRES_DW_CONN_ID)
        
        
        sources = {
            sql_output_dir: TABLES_TO_EXTRACT,
            os.path.dirname(csv_output_path): ['transacoes'] 
        }

        for source_dir, tables in sources.items():# percorre os diretórios de saída e carrega os dados para o DW
            for table_name in tables:
                file_path = os.path.join(source_dir, f"{table_name}.csv")
                
                if not os.path.exists(file_path):
                    print(f"Arquivo {file_path} não encontrado. Pulando.") #verificação de existência do arquivo
                    continue

                print(f"Iniciando carregamento para a tabela '{table_name}' do DW a partir de '{file_path}'")
                
                truncate_sql = f"TRUNCATE TABLE public.{table_name} RESTART IDENTITY;" #TRUNCATE para evitar duplicaçoes de registros (idempotencia)
                pg_dw_hook.run(truncate_sql)
                print(f"Tabela 'public.{table_name}' truncada.")

                copy_sql = f"COPY public.{table_name} FROM STDIN WITH CSV HEADER" #COPY para carregar os dados
                pg_dw_hook.copy_expert(sql=copy_sql, filename=file_path) #carrega os dados do arquivo CSV para a tabela do DW
                print(f"Carga da tabela 'public.{table_name}' concluída com sucesso.")
                #Mostrar banvic

    daily_output_dirs = create_daily_output_dirs()
    
    # Extração
    csv_extraction_path = extract_from_csv(daily_output_dirs)
    sql_extraction_path = extract_from_postgres(daily_output_dirs)

    # Carga
    load_to_data_warehouse(
        csv_output_path=csv_extraction_path,
        sql_output_dir=sql_extraction_path
    )


banvic_pipeline_dag = banvic_pipeline()