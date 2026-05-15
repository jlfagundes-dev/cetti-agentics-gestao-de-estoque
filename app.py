import os
import streamlit as st
from supabase_client import get_supabase_client

st.set_page_config(page_title="Cetti - Gestão de Estoque", layout="wide")


def get_clients(supabase):
    res = supabase.table("clientes").select("id,nome_empresa,slug").order("nome_empresa").execute()
    if getattr(res, "error", None):
        st.error(f"Erro ao buscar clientes: {res.error}")
        return []
    return res.data or []


def get_products(supabase, cliente_id=None):
    q = supabase.table("produtos").select("*")
    if cliente_id:
        q = q.eq("cliente_id", cliente_id)
    res = q.order("especie").execute()
    if getattr(res, "error", None):
        st.error(f"Erro ao buscar produtos: {res.error}")
        return []
    return res.data or []


def create_movimentacao(supabase, cliente_id, produto_id, tipo, quantidade, responsavel):
    # Busca estoque atual
    cur = supabase.table("produtos").select("estoque_atual").eq("id", produto_id).single().execute()
    if getattr(cur, "error", None):
        return {"error": f"Erro ao obter produto: {cur.error}"}
    estoque_atual = float(cur.data.get("estoque_atual", 0))
    if tipo == "entrada":
        novo = estoque_atual + float(quantidade)
    else:
        novo = estoque_atual - float(quantidade)
        if novo < 0:
            return {"error": "Estoque insuficiente"}

    # Atualiza produto
    up = supabase.table("produtos").update({"estoque_atual": novo}).eq("id", produto_id).execute()
    if getattr(up, "error", None):
        return {"error": f"Erro ao atualizar produto: {up.error}"}

    # Insere movimentacao
    payload = {
        "cliente_id": cliente_id,
        "produto_id": produto_id,
        "tipo_movimentacao": tipo,
        "quantidade": quantidade,
        "responsavel": responsavel,
    }
    ins = supabase.table("movimentacoes").insert(payload).execute()
    if getattr(ins, "error", None):
        return {"error": f"Erro ao inserir movimentacao: {ins.error}"}
    return {"ok": True}


def main():
    st.title("Cetti — Gestão de Estoque")

    try:
        supabase = get_supabase_client()
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

    # Simple sidebar navigation
    st.sidebar.title("Navegação")
    if st.sidebar.button("Início"):
        st.session_state.step = "init"
    if st.sidebar.button("Login"):
        st.session_state.step = "login"
    if st.sidebar.button("Responsável"):
        st.session_state.step = "responsavel"
    if st.sidebar.button("Dashboard"):
        st.session_state.step = "dashboard"
    if st.sidebar.button("Movimentação"):
        st.session_state.step = "movimentacao"

    # Step: Init
    if st.session_state.step == "init":
        st.header("Bem-vindo")
        st.write("Clique em Login para iniciar a sessão do tenant.")

    # Step: Login
    if st.session_state.step == "login":
        st.header("Login")
        pwd = st.text_input("Senha do app (APP_PASSWORD)", type="password")
        app_pwd = os.environ.get("APP_PASSWORD")
        if st.button("Entrar"):
            if app_pwd and pwd != app_pwd:
                st.error("Senha inválida")
            else:
                # Listar clientes e selecionar
                clients = get_clients(supabase)
                options = {c["nome_empresa"]: c["id"] for c in clients}
                sel = st.selectbox("Selecione o cliente", options=list(options.keys()))
                if sel:
                    st.session_state.cliente_id = options[sel]
                    st.success("Cliente selecionado e login realizado")
                    st.session_state.step = "responsavel"

    # Step: Responsável
    if st.session_state.step == "responsavel":
        st.header("Seleção de responsável")
        # tentar buscar responsáveis existentes (movimentacoes)
        res = supabase.table("movimentacoes").select("responsavel").order("created_at", desc=True).limit(50).execute()
        existing = []
        if not getattr(res, "error", None):
            existing = [r.get("responsavel") for r in res.data if r.get("responsavel")]
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
        products = get_products(supabase, st.session_state.cliente_id)
        if products:
            st.table(products)
        else:
            st.info("Nenhum produto encontrado para o cliente selecionado.")
        if st.button("Nova movimentação"):
            st.session_state.step = "movimentacao"

    # Step: Movimentação
    if st.session_state.step == "movimentacao":
        st.header("Registro de movimentação")
        products = get_products(supabase, st.session_state.cliente_id)
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
                out = create_movimentacao(supabase, st.session_state.cliente_id, produto_id, tipo, quantidade, responsavel)
                if out.get("error"):
                    st.error(out.get("error"))
                else:
                    st.success("Movimentação registrada")
                    st.session_state.step = "dashboard"


if __name__ == "__main__":
    main()
