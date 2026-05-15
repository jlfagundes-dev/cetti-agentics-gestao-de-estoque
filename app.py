import os
import streamlit as st
from supabase_client import get_supabase_config, rest_get, rest_patch, rest_post

st.set_page_config(page_title="Cetti - Gestão de Estoque", layout="wide")


def get_app_password() -> str | None:
    pwd = os.environ.get("APP_PASSWORD")
    if pwd:
        return pwd

    try:
        secret_pwd = st.secrets.get("APP_PASSWORD")
        if secret_pwd:
            return str(secret_pwd)
    except Exception:
        return None

    return None


def get_clients():
    params = {
        "select": "id,nome_empresa,slug",
        "order": "nome_empresa.asc",
    }
    return rest_get("clientes", params)


def get_products(cliente_id=None):
    params = {
        "select": "*",
        "order": "especie.asc",
    }
    if cliente_id:
        params["cliente_id"] = f"eq.{cliente_id}"
    return rest_get("produtos", params)


def get_parametros(cliente_id, tipo):
    params = {
        "select": "valor",
        "cliente_id": f"eq.{cliente_id}",
        "tipo": f"eq.{tipo}",
        "order": "valor.asc",
    }
    rows = rest_get("parametros", params)
    return [row.get("valor") for row in rows if row.get("valor")]


def get_responsaveis(cliente_id=None):
    params = {
        "select": "responsavel",
        "order": "created_at.desc",
        "limit": 100,
    }
    if cliente_id:
        params["cliente_id"] = f"eq.{cliente_id}"

    res_data = rest_get("movimentacoes", params)
    seen = []
    for r in res_data:
        name = r.get("responsavel")
        if name and name not in seen:
            seen.append(name)
    return seen


def create_movimentacao(cliente_id, produto_id, tipo, quantidade, responsavel):
    # Busca estoque atual via Data API
    produto_rows = rest_get(
        "produtos",
        {
            "select": "id,estoque_atual",
            "id": f"eq.{produto_id}",
            "cliente_id": f"eq.{cliente_id}",
            "limit": 1,
        },
    )
    if not produto_rows:
        return {"error": "Produto não encontrado para o cliente selecionado"}

    estoque_atual = float(produto_rows[0].get("estoque_atual", 0))
    if tipo == "entrada":
        novo = estoque_atual + float(quantidade)
    else:
        novo = estoque_atual - float(quantidade)
        if novo < 0:
            return {"error": "Estoque insuficiente"}

    # Atualiza produto
    rest_patch(
        "produtos",
        {"estoque_atual": novo},
        {
            "id": f"eq.{produto_id}",
            "cliente_id": f"eq.{cliente_id}",
        },
    )

    # Insere movimentacao
    payload = {
        "cliente_id": cliente_id,
        "produto_id": produto_id,
        "tipo_movimentacao": tipo.lower(),
        "quantidade": quantidade,
        "responsavel": responsavel,
    }
    rest_post("movimentacoes", payload)
    return {"ok": True}


def main():
    st.title("Cetti — Gestão de Estoque")

    try:
        get_supabase_config()
    except Exception as e:
        st.error(str(e))
        return

    # Inicializa estado
    if "step" not in st.session_state:
        st.session_state.step = "init"
    if "cliente_id" not in st.session_state:
        st.session_state.cliente_id = ""
    if "responsavel" not in st.session_state:
        st.session_state.responsavel = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Simple sidebar navigation (enforce sequential flow)
    st.sidebar.title("Navegação")
    if st.sidebar.button("Início"):
        st.session_state.step = "init"
    # Login sempre acessível a partir do início
    if st.sidebar.button("Login"):
        st.session_state.step = "login"
    # Demais passos só se cumpridos os anteriores
    if st.sidebar.button("Responsável"):
        if not st.session_state.get("logged_in") or not st.session_state.get("cliente_id"):
            st.warning("Faça login primeiro e selecione um cliente")
        else:
            st.session_state.step = "responsavel"
    if st.sidebar.button("Dashboard"):
        if not st.session_state.get("responsavel"):
            st.warning("Defina o responsável antes de acessar o dashboard")
        else:
            st.session_state.step = "dashboard"
    if st.sidebar.button("Movimentação"):
        if not st.session_state.get("responsavel"):
            st.warning("Defina o responsável antes de registrar movimentações")
        else:
            st.session_state.step = "movimentacao"

    # Step: Init
    if st.session_state.step == "init":
        st.header("Bem-vindo")
        st.write("Clique em Login para iniciar a sessão do tenant.")

    # Step: Login
    if st.session_state.step == "login":
        st.header("Login")
        pwd = st.text_input("Senha do app (APP_PASSWORD)", type="password")
        clients = []
        clients_error = None
        try:
            clients = get_clients()
        except Exception as ex:
            clients_error = str(ex)

        if clients_error:
            st.error(f"Erro ao buscar clientes na Data API: {clients_error}")

        clients_by_id = {c.get("id"): c for c in clients if c.get("id")}
        client_ids = [""] + list(clients_by_id.keys())
        selected_cliente_id = st.selectbox(
            "Cliente",
            options=client_ids,
            index=0,
            format_func=lambda cid: "Selecione..."
            if not cid
            else f"{clients_by_id[cid].get('nome_empresa')} ({clients_by_id[cid].get('slug')})",
        )

        app_pwd = get_app_password()
        if st.button("Entrar"):
            if app_pwd and pwd != app_pwd:
                st.error("Senha inválida")
            elif not selected_cliente_id:
                st.warning("Selecione um cliente")
            else:
                if selected_cliente_id not in clients_by_id:
                    st.warning("Seleção de cliente inválida")
                else:
                    st.session_state.cliente_id = selected_cliente_id
                    st.session_state.logged_in = True
                    st.success("Login realizado")
                    st.session_state.step = "responsavel"

    # Step: Responsável
    if st.session_state.step == "responsavel":
        st.header("Seleção de responsável")
        existing = []
        try:
            existing = get_responsaveis(st.session_state.cliente_id)
        except Exception as ex:
            st.warning(f"Não foi possível carregar responsáveis existentes: {ex}")

        responsavel = st.selectbox("Responsável (selecione ou digite novo)", options=[""] + existing)
        if responsavel == "":
            responsavel = st.text_input("Digite o nome do responsável")
        if st.button("Confirmar responsável"):
            if not responsavel:
                st.warning("Informe o nome do responsável")
            else:
                st.session_state.responsavel = responsavel
                st.success("Responsável definido")
                st.session_state.step = "dashboard"

    # Step: Dashboard
    if st.session_state.step == "dashboard":
        st.header("Dashboard")
        st.subheader("Produtos / Saldos")
        try:
            products = get_products(st.session_state.cliente_id)
        except Exception as ex:
            st.error(f"Erro ao carregar produtos: {ex}")
            products = []

        if products:
            st.table(products)
        else:
            st.info("Nenhum produto encontrado para o cliente selecionado.")
        if st.button("Nova movimentação"):
            st.session_state.step = "movimentacao"

    # Step: Movimentação
    if st.session_state.step == "movimentacao":
        st.header("Registro de movimentação")
        try:
            products = get_products(st.session_state.cliente_id)
        except Exception as ex:
            st.error(f"Erro ao carregar produtos: {ex}")
            products = []

        prod_options = {p.get("especie") + " — " + p.get("id")[:8]: p.get("id") for p in products}
        prod_sel = st.selectbox("Produto", options=[""] + list(prod_options.keys()))
        tipo = st.selectbox("Tipo", ["entrada", "saida"])
        quantidade = st.number_input("Quantidade", min_value=0.0, format="%.2f")
        responsavel = st.session_state.get("responsavel") or st.text_input("Responsável")
        if st.button("Salvar movimentação"):
            produto_id = prod_options.get(prod_sel)
            if not produto_id:
                st.warning("Selecione um produto")
            elif not responsavel:
                st.warning("Informe o responsável")
            else:
                try:
                    out = create_movimentacao(
                        st.session_state.cliente_id,
                        produto_id,
                        tipo,
                        quantidade,
                        responsavel,
                    )
                    if out.get("error"):
                        st.error(out.get("error"))
                    else:
                        st.success("Movimentação registrada")
                        st.session_state.step = "dashboard"
                except Exception as ex:
                    st.error(f"Erro ao salvar movimentação: {ex}")


if __name__ == "__main__":
    main()
