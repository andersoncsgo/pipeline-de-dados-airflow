# Desafio de Engenharia de Dados - Banco Vitória (BanVic)

Este projeto implementa um pipeline de dados para o banco fictício BanVic, conforme especificado no desafio de Engenharia de Dados. O pipeline extrai dados de um banco de dados PostgreSQL e de um arquivo CSV, os armazena em um sistema de arquivos local e os carrega em um Data Warehouse PostgreSQL. A orquestração é feita com Apache Airflow.

## Visão Geral da Solução

A solução é totalmente conteinerizada usando Docker e Docker Compose, garantindo total reprodutibilidade em qualquer ambiente com Docker instalado.

O pipeline é definido em uma única DAG do Airflow (`banvic_pipeline.py`) que realiza as seguintes etapas:
1.  **Criação de Diretórios**: Cria uma estrutura de pastas para a execução do dia no formato `YYYY-MM-DD/`.
2.  **Extração Paralela**:
    * Extrai dados de tabelas do banco de dados de origem (PostgreSQL) para arquivos CSV.
    * Extrai dados de um arquivo `transacoes.csv` para um novo arquivo CSV.
3.  **Carregamento no Data Warehouse**: Após o sucesso de ambas as extrações, carrega os dados dos arquivos CSV gerados para as tabelas correspondentes no Data Warehouse (PostgreSQL).

## Estrutura do Projeto

```
.
├── dags/                     # Contém a DAG do Airflow (banvic_pipeline.py)
├── data/                     # Local para o arquivo fonte transacoes.csv
├── output/                   # Diretório onde os CSVs extraídos são salvos
├── scripts/                  # Scripts SQL para inicialização do DW
├── banvic.sql                # Dump SQL do banco de dados fonte
├── docker-compose.yml        # Orquestra todos os serviços (Airflow, DBs)
└── README.md                 # Este documento
```

## Pré-requisitos

-   Docker
-   Docker Compose

## Instruções de Execução

1.  **Clone ou Descompacte o Projeto**: Garanta que você tenha todos os arquivos na estrutura de pastas descrita acima.

2.  **Posicione os Arquivos Fonte**:
    * Coloque o arquivo `transacoes.csv` dentro da pasta `data/`.
    * Verifique se o arquivo `banvic.sql` está na raiz do projeto.

3.  **Inicie o Ambiente**: Abra um terminal na pasta raiz do projeto (`LH_DE_SEUNOME/`) e execute o seguinte comando:
    ```bash
    docker-compose up -d --build
    ```
    Este comando irá:
    * Construir as imagens dos contêineres, se necessário.
    * Iniciar todos os serviços em segundo plano (`-d`):
        * Banco de dados fonte em `localhost:55432`.
        * Data Warehouse em `localhost:55433`.
        * Apache Airflow Webserver em `localhost:8080`.

4.  **Acesse a UI do Airflow**:
    * Abra seu navegador e acesse `http://localhost:8080`.
    * Pode levar alguns minutos para que o webserver esteja totalmente operacional.
    * Use o usuário `airflow` e a senha `airflow` para fazer login.

5.  **Execute a DAG**:
    * Na interface do Airflow, você verá a DAG `banvic_data_pipeline`.
    * Ative a DAG clicando no botão de alternância à esquerda do nome da DAG.
    * Para uma execução manual, clique no botão "Play" (▶️) à direita e selecione "Trigger DAG".

6.  **Verifique os Resultados**:
    * **Arquivos Extraídos**: Após a execução bem-sucedida das tarefas de extração, navegue até a pasta `output/` no seu computador. Você encontrará uma nova pasta com a data da execução (ex: `2025-09-02/`) contendo os subdiretórios `csv_source` e `sql_source` com os respectivos arquivos CSV.
    * **Dados no Data Warehouse**: Use uma ferramenta de banco de dados de sua preferência (como DBeaver, DataGrip ou `psql`) para se conectar ao Data Warehouse e verificar se os dados foram carregados.
        * **Host**: `localhost`
        * **Porta**: `55433`
        * **Banco de Dados**: `banvic_dw`
        * **Usuário**: `dw_user`
        * **Senha**: `dw_password`
        
        Execute consultas como `SELECT COUNT(*) FROM public.clientes;` ou `SELECT * FROM public.transacoes LIMIT 10;` para confirmar que os dados estão presentes.