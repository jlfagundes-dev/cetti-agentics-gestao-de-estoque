import html
import os

import pandas as pd
import streamlit as st

from supabase_client import get_supabase_config, rest_get, rest_patch, rest_post


st.set_page_config(page_title="Cetti - Gestão de Estoque", layout="wide")

# Injeção de CSS para ocultar os menus padrão do Streamlit (Fork, Perfil, Status)
st.markdown(
    """
    <style>
    /* Oculta o botão de Fork e o ícone do GitHub no topo */
    .stAppToolbar, div[data-testid="stStatusWidget"], .stDeployButton, a[href*="github.com"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Oculta o menu de três pontinhos (...) no canto superior direito */
    #MainMenu {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* Oculta o rodapé e as informações de perfil do GitHub no canto inferior direito */
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    div[data-testid="stDecoration"], div[data-testid="stCloudAppViewerHeader"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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


def get_clients() -> list[dict[str, object]]:
    params = {
        "select": "id,nome_empresa,slug",
        "order": "nome_empresa.asc",
    }
    return rest_get("clientes", params)


def get_products(cliente_id: str) -> list[dict[str, object]]:
    if not cliente_id:
        return []

    params = {
        "select": "id,cliente_id,especie,tipo_peca,dimensoes,unidade_medida,preco_unitario,estoque_atual",
        "cliente_id": f"eq.{cliente_id}",
        "order": "especie.asc",
    }
    return rest_get("produtos", params)


def get_parametros(cliente_id: str, tipo: str) -> list[str]:
    if not cliente_id:
        return []

    params = {
        "select": "valor",
        "cliente_id": f"eq.{cliente_id}",
        "tipo": f"eq.{tipo}",
        "order": "valor.asc",
    }
    rows = rest_get("parametros", params)
    return [row.get("valor") for row in rows if row.get("valor")]


def get_responsaveis(cliente_id: str) -> list[str]:
    if not cliente_id:
        return []

    params = {
        "select": "responsavel",
        "cliente_id": f"eq.{cliente_id}",
        "order": "created_at.desc",
        "limit": 100,
    }
    res_data = rest_get("movimentacoes", params)
    seen = []
    for row in res_data:
        name = row.get("responsavel")
        if name and name not in seen:
            seen.append(name)
    return seen


def get_entidades(cliente_id: str, tipo_entidade: str) -> list[dict[str, object]]:
    if not cliente_id or not tipo_entidade:
        return []

    params = {
        "select": "id,nome_razao,tipo_entidade,documento",
        "cliente_id": f"eq.{cliente_id}",
        "tipo_entidade": f"eq.{tipo_entidade}",
        "order": "nome_razao.asc",
    }
    return rest_get("entidades", params)


def format_product_label(product: dict[str, object]) -> str:
    parts = [
        str(product.get("especie") or "Produto"),
        str(product.get("tipo_peca") or ""),
        str(product.get("dimensoes") or ""),
        str(product.get("unidade_medida") or ""),
    ]
    return " - ".join(part for part in parts if part)


def format_entidade_label(entidade: dict[str, object]) -> str:
    parts = [str(entidade.get("nome_razao") or "Parceiro")]
    if entidade.get("documento"):
        parts.append(str(entidade.get("documento")))
    return " - ".join(parts)


def format_currency_brl(value: object) -> str:
    try:
        numeric_value = float(value or 0)
    except (TypeError, ValueError):
        numeric_value = 0.0

    formatted = f"{numeric_value:,.2f}"
    formatted = formatted.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


def dashboard_products_view(products: list[dict[str, object]]) -> list[dict[str, object]]:
    visible_rows: list[dict[str, object]] = []
    for product in products:
        visible_rows.append(
            {
                "Espécie": product.get("especie"),
                "Tipo de peça": product.get("tipo_peca"),
                "Dimensões": product.get("dimensoes"),
                "Unidade": product.get("unidade_medida"),
                "Preço unitário": format_currency_brl(product.get("preco_unitario")),
                "Estoque atual": product.get("estoque_atual"),
            }
        )
    return visible_rows


def parceiros_view(parceiros: list[dict[str, object]]) -> list[dict[str, object]]:
    visible_rows: list[dict[str, object]] = []
    for entidade in parceiros:
        visible_rows.append(
            {
                "Nome / Razão Social": entidade.get("nome_razao"),
                "Tipo": entidade.get("tipo_entidade"),
                "Documento": entidade.get("documento"),
                "Telefone": entidade.get("telefone"),
                "Email": entidade.get("email"),
            }
        )
    return visible_rows


def render_left_aligned_table(rows: list[dict[str, object]]) -> None:
    if not rows:
        st.info("Nenhum item para exibir.")
        return

    def cell_text(value: object) -> str:
        if value is None:
            return ""
        if pd.isna(value):
            return ""
        return str(value)

    dataframe = pd.DataFrame(rows)
    headers = list(dataframe.columns)
    header_html = "".join(
        f'<th style="text-align:left;padding:0.5rem 0.75rem;border-bottom:1px solid #ddd;">{html.escape(str(header))}</th>'
        for header in headers
    )
    body_rows = []
    for _, row in dataframe.iterrows():
        cells = "".join(
            f'<td style="text-align:left;padding:0.5rem 0.75rem;border-bottom:1px solid #f0f0f0;">{html.escape(cell_text(row[header]))}</td>'
            for header in headers
        )
        body_rows.append(f"<tr>{cells}</tr>")

    table_html = """
    <div style="overflow-x:auto; width:100%;">
      <table style="width:100%; border-collapse:collapse; text-align:left;">
        <thead><tr>{header_html}</tr></thead>
        <tbody>{body_rows}</tbody>
      </table>
    </div>
    """.format(header_html=header_html, body_rows="".join(body_rows))
    st.markdown(table_html, unsafe_allow_html=True)


def create_entidade(
    cliente_id: str,
    nome_razao: str,
    tipo_entidade: str,
    documento: str,
    telefone: str = "",
    email: str = "",
) -> list[dict[str, object]]:
    if not cliente_id:
        return []

    payload = {
        "cliente_id": cliente_id,
        "nome_razao": nome_razao.strip(),
        "tipo_entidade": tipo_entidade.strip(),
        "documento": documento.strip() or None,
        "telefone": telefone.strip() or None,
        "email": email.strip() or None,
    }
    return rest_post("entidades", payload)


def create_movimentacao(
    cliente_id: str,
    produto_id: str,
    tipo: str,
    quantidade: float,
    responsavel: str,
    entidade_id: str | None,
    natureza_operacao: str,
) -> dict[str, object]:
    if not cliente_id:
        return {"error": "Cliente não selecionado"}

    if quantidade <= 0:
        return {"error": "Informe uma quantidade maior que zero"}

    produto_rows = rest_get(
        "produtos",
        {
            "select": "id,cliente_id,estoque_atual,preco_unitario",
            "id": f"eq.{produto_id}",
            "cliente_id": f"eq.{cliente_id}",
            "limit": 1,
        },
    )
    if not produto_rows:
        return {"error": "Produto não encontrado para o cliente selecionado"}

    produto = produto_rows[0]
    estoque_atual = float(produto.get("estoque_atual") or 0)
    preco_unitario = float(produto.get("preco_unitario") or 0)

    if tipo == "saida" and quantidade > estoque_atual:
        return {"error": "Estoque insuficiente"}

    if tipo == "entrada":
        novo_estoque = estoque_atual + float(quantidade)
    else:
        novo_estoque = estoque_atual - float(quantidade)

    updated_rows = rest_patch(
        "produtos",
        {"estoque_atual": novo_estoque},
        {
            "id": f"eq.{produto_id}",
            "cliente_id": f"eq.{cliente_id}",
        },
    )
    if not updated_rows:
        return {"error": "Não foi possível atualizar o estoque do produto"}

    valor_monetario_total = float(quantidade) * preco_unitario
    payload = {
        "cliente_id": cliente_id,
        "produto_id": produto_id,
        "tipo_movimentacao": tipo,
        "natureza_operacao": natureza_operacao,
        "entidade_id": entidade_id or None,
        "quantidade": quantidade,
        "valor_monetario_total": valor_monetario_total,
        "responsavel": responsavel,
    }
    rest_post("movimentacoes", payload)
    return {"ok": True, "valor_monetario_total": valor_monetario_total}


def logout() -> None:
    st.session_state.step = "init"
    st.session_state.cliente_id = ""
    st.session_state.responsavel = ""
    st.session_state.logged_in = False


def ensure_session_state() -> None:
    defaults = {
        "step": "init",
        "cliente_id": "",
        "responsavel": "",
        "logged_in": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sidebar_navigation() -> None:
    st.sidebar.title("Navegação")

    if st.session_state.step == "init":
        st.sidebar.button("Início", disabled=True)
    else:
        if st.sidebar.button("Início"):
            st.session_state.step = "init"

    if st.sidebar.button("Login"):
        st.session_state.step = "login"

    if st.session_state.get("logged_in"):
        if st.sidebar.button("Sair"):
            logout()
            st.rerun()

    if st.session_state.get("responsavel"):
        if st.sidebar.button("📊 Dashboard"):
            st.session_state.step = "dashboard"
        if st.sidebar.button("🤝 Cadastrar Parceiros"):
            st.session_state.step = "parceiros"
        if st.sidebar.button("🪵 Movimentar Estoque"):
            st.session_state.step = "movimentacao"


def render_init() -> None:
    st.header("Bem-vindo")
    st.write("Clique em Login para iniciar a sessão do tenant.")


def render_login() -> None:
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

    clients_by_id = {client.get("id"): client for client in clients if client.get("id")}
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
        elif selected_cliente_id not in clients_by_id:
            st.warning("Seleção de cliente inválida")
        else:
            st.session_state.cliente_id = selected_cliente_id
            st.session_state.logged_in = True
            st.session_state.step = "responsavel"
            st.success("Login realizado")
            st.rerun()


def render_responsavel() -> None:
    st.header("Seleção de responsável")

    existing = []
    try:
        existing = get_responsaveis(st.session_state.cliente_id)
    except Exception as ex:
        st.warning(f"Não foi possível carregar responsáveis existentes: {ex}")

    responsavel = st.selectbox("Responsável cadastrado", options=[""] + existing)
    if responsavel == "":
        responsavel = st.text_input("Digite o nome do responsável")

    if st.button("Confirmar responsável"):
        if not responsavel:
            st.warning("Informe o nome do responsável")
        else:
            st.session_state.responsavel = responsavel
            st.session_state.step = "dashboard"
            st.success("Responsável definido")
            st.rerun()


def render_dashboard() -> None:
    st.header("Dashboard")
    st.subheader("Produtos / Saldos")

    try:
        products = get_products(st.session_state.cliente_id)
    except Exception as ex:
        st.error(f"Erro ao carregar produtos: {ex}")
        products = []

    if products:
        render_left_aligned_table(dashboard_products_view(products))
    else:
        st.info("Nenhum produto encontrado para o cliente selecionado.")


def render_parceiros() -> None:
    st.header("Cadastrar Parceiros")

    with st.form("form_parceiro", clear_on_submit=True):
        nome_razao = st.text_input("Nome / Razão Social")
        tipo_entidade = st.selectbox("Tipo de parceiro", options=["", "cliente", "fornecedor"])
        documento = st.text_input("CPF / CNPJ (opcional)")
        telefone = st.text_input("Telefone (opcional)")
        email = st.text_input("Email (opcional)")
        submitted = st.form_submit_button("Salvar parceiro")

    if submitted:
        if not nome_razao.strip():
            st.error("Informe o nome ou razão social")
            return
        if not tipo_entidade:
            st.error("Selecione o tipo de parceiro")
            return

        try:
            result = create_entidade(
                st.session_state.cliente_id,
                nome_razao,
                tipo_entidade,
                documento,
                telefone,
                email,
            )
            if result:
                st.success("Parceiro cadastrado com sucesso")
            else:
                st.error("Não foi possível cadastrar o parceiro")
        except Exception as ex:
            st.error(f"Erro ao cadastrar parceiro: {ex}")

    st.subheader("Parceiros cadastrados")
    try:
        clientes = get_entidades(st.session_state.cliente_id, "cliente")
        fornecedores = get_entidades(st.session_state.cliente_id, "fornecedor")
        parceiros = clientes + fornecedores
    except Exception as ex:
        st.error(f"Erro ao carregar parceiros: {ex}")
        parceiros = []

    if parceiros:
        render_left_aligned_table(parceiros_view(parceiros))
    else:
        st.info("Nenhum parceiro encontrado para o cliente selecionado.")


def render_movimentacao() -> None:
    st.header("Movimentar Estoque")

    try:
        products = get_products(st.session_state.cliente_id)
    except Exception as ex:
        st.error(f"Erro ao carregar produtos: {ex}")
        products = []

    tipo = st.selectbox("Tipo de movimentação", options=["entrada", "saida"])
    natureza_operacao = "compra" if tipo == "entrada" else "venda"
    st.text_input("Natureza da operação", value=natureza_operacao, disabled=True)

    entidade_tipo = "fornecedor" if tipo == "entrada" else "cliente"
    entidades = get_entidades(st.session_state.cliente_id, entidade_tipo)
    entidade_map = {
        format_entidade_label(entidade): entidade.get("id")
        for entidade in entidades
        if entidade.get("id")
    }
    entidade_label = st.selectbox(
        f"{entidade_tipo.capitalize()}",
        options=[""] + list(entidade_map.keys()),
    )

    product_map = {
        format_product_label(product): product
        for product in products
        if product.get("id")
    }
    product_label = st.selectbox("Produto", options=[""] + list(product_map.keys()))
    quantidade = st.number_input("Quantidade", min_value=0.0, format="%.2f")
    responsavel = st.session_state.get("responsavel") or st.text_input("Responsável")

    if st.button("Salvar movimentação"):
        produto = product_map.get(product_label)
        entidade_id = entidade_map.get(entidade_label)

        if not produto:
            st.warning("Selecione um produto")
            return
        if not entidade_id:
            st.warning("Selecione um parceiro")
            return
        if not responsavel:
            st.warning("Informe o responsável")
            return

        try:
            out = create_movimentacao(
                st.session_state.cliente_id,
                str(produto.get("id")),
                tipo,
                quantidade,
                responsavel,
                entidade_id,
                natureza_operacao,
            )
            if out.get("error"):
                st.error(out.get("error"))
            else:
                total_formatado = format_currency_brl(out.get("valor_monetario_total"))
                st.success(f"Movimentação registrada. Total: {total_formatado}")
                st.session_state.step = "dashboard"
        except Exception as ex:
            st.error(f"Erro ao salvar movimentação: {ex}")


def main() -> None:
    st.title("Cetti — Gestão de Estoque")

    try:
        get_supabase_config()
    except Exception as exc:
        st.error(str(exc))
        return

    ensure_session_state()
    sidebar_navigation()

    if st.session_state.step == "init":
        render_init()
    elif st.session_state.step == "login":
        render_login()
    elif st.session_state.step == "responsavel":
        render_responsavel()
    elif st.session_state.step == "dashboard":
        render_dashboard()
    elif st.session_state.step == "parceiros":
        render_parceiros()
    elif st.session_state.step == "movimentacao":
        render_movimentacao()
    else:
        st.session_state.step = "dashboard" if st.session_state.get("responsavel") else "responsavel"
        st.rerun()


if __name__ == "__main__":
    main()
