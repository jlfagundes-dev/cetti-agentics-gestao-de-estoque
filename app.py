import os
import streamlit as st
from supabase_client import get_supabase_client

st.set_page_config(page_title="Cetti - Gestão de Estoque", layout="wide")

def load_products(supabase):
    res = supabase.table("products").select("*").order("id").execute()
    if res.error:
        st.error(f"Erro ao buscar produtos: {res.error}")
        return []
    return res.data or []

def insert_product(supabase, name, quantity, price):
    payload = {"name": name, "quantity": quantity, "price": price}
    res = supabase.table("products").insert(payload).execute()
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
        name = st.text_input("Nome")
        quantity = st.number_input("Quantidade", min_value=0, value=0)
        price = st.number_input("Preço", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            if not name:
                st.warning("Informe o nome do produto")
            else:
                res = insert_product(supabase, name, int(quantity), float(price))
                if res.error:
                    st.error(f"Erro ao inserir: {res.error}")
                else:
                    st.success("Produto adicionado")

    products = load_products(supabase)

    st.subheader("Produtos")
    if products:
        st.table(products)
    else:
        st.info("Nenhum produto encontrado.")

if __name__ == "__main__":
    main()
