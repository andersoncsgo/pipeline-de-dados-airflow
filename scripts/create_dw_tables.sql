
\c banvic_dw;


CREATE TYPE public.status_proposta AS ENUM (
    'Enviada',
    'Validação documentos',
    'Aprovada',
    'Reprovada',
    'Em análise'
);

CREATE TYPE public.tipo_agencia AS ENUM (
    'Digital',
    'Física'
);

CREATE TYPE public.tipo_cliente AS ENUM (
    'PF',
    'PJ'
);

CREATE TABLE IF NOT EXISTS public.transacoes (
    cod_transacao INTEGER PRIMARY KEY,
    num_conta BIGINT,
    data_transacao TIMESTAMP WITH TIME ZONE,
    nome_transacao VARCHAR(255),
    valor_transacao NUMERIC(15, 2)
);


CREATE TABLE IF NOT EXISTS public.agencias (
    cod_agencia INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    endereco TEXT,
    cidade VARCHAR(255),
    uf CHAR(2),
    data_abertura DATE,
    tipo_agencia public.tipo_agencia
);

CREATE TABLE IF NOT EXISTS public.clientes (
    cod_cliente INTEGER PRIMARY KEY,
    primeiro_nome VARCHAR(255) NOT NULL,
    ultimo_nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    tipo_cliente public.tipo_cliente,
    data_inclusao TIMESTAMP WITH TIME ZONE,
    cpfcnpj VARCHAR(18) NOT NULL,
    data_nascimento DATE,
    endereco TEXT,
    cep VARCHAR(9)
);

CREATE TABLE IF NOT EXISTS public.colaboradores (
    cod_colaborador INTEGER PRIMARY KEY,
    primeiro_nome VARCHAR(255) NOT NULL,
    ultimo_nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    data_nascimento DATE,
    endereco TEXT,
    cep VARCHAR(9)
);

CREATE TABLE IF NOT EXISTS public.contas (
    num_conta BIGINT PRIMARY KEY,
    cod_cliente INTEGER,
    cod_agencia INTEGER,
    cod_colaborador INTEGER,
    tipo_conta public.tipo_cliente,
    data_abertura TIMESTAMP WITH TIME ZONE,
    saldo_total NUMERIC(15,2),
    saldo_disponivel NUMERIC(15,2),
    data_ultimo_lancamento TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS public.propostas_credito (
    cod_proposta INTEGER PRIMARY KEY,
    cod_cliente INTEGER,
    cod_colaborador INTEGER,
    data_entrada_proposta TIMESTAMP WITH TIME ZONE,
    taxa_juros_mensal NUMERIC(5,4),
    valor_proposta NUMERIC(15,2),
    valor_financiamento NUMERIC(15,2),
    valor_entrada NUMERIC(15,2),
    valor_prestacao NUMERIC(15,2),
    quantidade_parcelas INTEGER,
    carencia INTEGER,
    status_proposta public.status_proposta
);

CREATE TABLE IF NOT EXISTS public.colaborador_agencia (
    cod_colaborador INTEGER,
    cod_agencia INTEGER,
    PRIMARY KEY (cod_colaborador, cod_agencia)
);