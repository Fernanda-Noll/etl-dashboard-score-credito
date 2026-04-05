import pandas as pd

dados_cliente = pd.read_csv(
    "dados/cliente.csv",
    dtype={"cpf": str},
)
dados_analise_credito = pd.read_csv("dados/analise_credito.csv")


# TRATAMENTO TABELA CLIENTE
def transformacao_tabela_cliente(dados_cliente):
    dados_cliente = dados_cliente.copy()
    # print(dados_cliente.dtypes)

    # Remove espaços
    dados_cliente.columns = dados_cliente.columns.str.strip()

    # Padroniza texto
    dados_cliente["nome"] = dados_cliente["nome"].str.strip().str.title()
    dados_cliente["sobrenome"] = dados_cliente["sobrenome"].str.strip().str.title()

    # Limpa CPF
    dados_cliente["cpf"] = dados_cliente["cpf"].str.replace(r"\D", "", regex=True)
    dados_cliente["cpf"] = dados_cliente["cpf"].replace("", pd.NA)

    # Padroniza datas
    dados_cliente["data_de_nascimento"] = pd.to_datetime(
        dados_cliente["data_de_nascimento"], errors="coerce"
    )

    # Remove nulos
    dados_cliente = dados_cliente.dropna(
        subset=["nome", "sobrenome", "data_de_nascimento", "cpf"]
    )

    # Remove CPFs duplicados
    dados_cliente = dados_cliente.drop_duplicates(subset="cpf", keep="first")

    # Coluna Idade e remoção de menores de 18 anos
    hoje = pd.Timestamp("2025-12-31")
    dados_cliente["idade"] = (hoje - dados_cliente["data_de_nascimento"]).dt.days // 365
    dados_cliente = dados_cliente[dados_cliente["idade"] >= 18]

    return dados_cliente


# TRATAMENTO TABELA ANALISE_CREDITO
def transformacao_tabela_analise_credito(dados_analise_credito, dados_cliente_tratados):
    dados_analise_credito = dados_analise_credito.copy()
    # print(dados_analise_credito.dtypes)

    # Remove os espaços
    dados_analise_credito.columns = dados_analise_credito.columns.str.strip()

    # Mantem os ids compativeis em ambas as tabelas
    dados_analise_credito = dados_analise_credito[
        dados_analise_credito["fk_id_cliente"].isin(
            dados_cliente_tratados["id_cliente"]
        )
    ]

    # Padroniza datas
    dados_analise_credito["data_consulta"] = pd.to_datetime(
        dados_analise_credito["data_consulta"], errors="coerce"
    )
    dados_analise_credito["data_atualizacao"] = pd.to_datetime(
        dados_analise_credito["data_atualizacao"], errors="coerce"
    )
    # Remove datas inválidas
    dados_analise_credito = dados_analise_credito.dropna(
        subset=["data_consulta", "data_atualizacao"]
    )

    # Valores nulos - apenas as que foram identificadas com valores nulos serão removidas 
    total_nulos_analise_credito = dados_analise_credito.isnull().sum()
    print(total_nulos_analise_credito)
    dados_analise_credito = dados_analise_credito.dropna(
        subset=["score_credito", "valor_credito"]
    )

    # Valores duplicados - não possui valores duplicados
    total_duplicados_analise_credito = dados_analise_credito.duplicated().sum()
    print(total_duplicados_analise_credito)
    dados_analise_credito = dados_analise_credito.drop_duplicates()

    # Data da consulta aconce primeiro que a atualização
    dados_analise_credito = dados_analise_credito[
        dados_analise_credito["data_consulta"]
        <= dados_analise_credito["data_atualizacao"]
    ]

    return dados_analise_credito


# CRIO OS ARQUIVOS TRATADOS
dados_cliente_tratados = transformacao_tabela_cliente(dados_cliente)
print(dados_cliente_tratados)
arquivo_dados_cliente_tratados = "dados/dados_cliente_tratados.csv"
dados_cliente_tratados.to_csv(arquivo_dados_cliente_tratados, index=False)

dados_analise_credito_tratados = transformacao_tabela_analise_credito(
    dados_analise_credito, dados_cliente_tratados
)
arquivo_dados_analise_credito_tratados = "dados/dados_analise_credito_tratados.csv"
dados_analise_credito_tratados.to_csv(
    arquivo_dados_analise_credito_tratados, index=False
)
