import os
import streamlit as st
from supabase_client import get_supabase_client

st.set_page_config(page_title="Cetti - Gestão de Estoque", layout="wide")

def load_products(supabase):
    cliente_id = st.session_state.get("cliente_id")
    query = supabase.table("produtos").select("*")
    if cliente_id:
        query = query.eq("cliente_id", cliente_id)
    res = query.order("id").execute()
    if getattr(res, "error", None):
        st.error(f"Erro ao buscar produtos: {res.error}")
        return []
    return res.data or []

def insert_product(supabase, cliente_id, especie, tipo_peca, dimensoes, unidade_medida, preco_unitario, estoque_atual):
    payload = {
        "cliente_id": cliente_id,
        "especie": especie,
        "tipo_peca": tipo_peca,
        "dimensoes": dimensoes,
        "unidade_medida": unidade_medida,
        "preco_unitario": preco_unitario,
        "estoque_atual": estoque_atual,
    }
    res = supabase.table("produtos").insert(payload).execute()
    return res

def main():
    st.title("Cetti — Gestão de Estoque")
    try:
        supabase = get_supabase_client()
    except Exception as e:
        st.error(str(e))
        return

    with st.sidebar.form("add_product"):
        st.header("Adicionar produto")
        cliente_input = st.text_input("Cliente ID (cliente_id)")
        especie = st.text_input("Espécie")
        tipo_peca = st.text_input("Tipo de peça")
        dimensoes = st.text_input("Dimensões")
        unidade_medida = st.text_input("Unidade de medida")
        preco_unitario = st.number_input("Preço unitário", min_value=0.0, format="%.2f")
        estoque_atual = st.number_input("Estoque inicial", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            cliente_id = cliente_input or st.session_state.get("cliente_id")
            if not cliente_id:
                st.warning("Informe o cliente_id na sidebar ou no campo Cliente ID")
            elif not especie or not tipo_peca or not unidade_medida:
                st.warning("Preencha os campos: Espécie, Tipo de peça e Unidade de medida")
            else:
                res = insert_product(
                    supabase,
                    cliente_id,
                    especie,
                    tipo_peca,
                    dimensoes,
                    unidade_medida,
                    float(preco_unitario),
                    float(estoque_atual),
                )
                if getattr(res, "error", None):
                    st.error(f"Erro ao inserir: {res.error}")
                else:
                    st.success("Produto adicionado")

    # Página principal: permitir definir cliente_id em sessão
    if "cliente_id" not in st.session_state:
        st.session_state["cliente_id"] = ""
    st.sidebar.markdown("---")
    sid_cli = st.sidebar.text_input("Cliente atual (cliente_id)", value=st.session_state.get("cliente_id", ""))
    if sid_cli != st.session_state.get("cliente_id"):
        st.session_state["cliente_id"] = sid_cli

    products = load_products(supabase)

    st.subheader("Produtos")
    if products:
        st.table(products)
    else:
        st.info("Nenhum produto encontrado.")

if __name__ == "__main__":
    main()
