# Cursor/Copilot Rules - MVP SaaS Estoque Madeireira

Este documento serve como instrução de contexto para o desenvolvimento do MVP de controle de estoque. Siga rigorosamente estas definições para manter a consistência do projeto.

## 1. Visão Geral do Projeto
- **Objetivo:** SaaS Multi-tenant para controle de estoque de madeireiras.
- **Stack:** Python (Streamlit), Supabase (PostgreSQL + Auth), GitHub (Hospedagem/CI).
- **Foco:** Mobile-first (uso em pátio), interface simples com botões grandes.
- **Prazo:** Entrega de MVP em 24h.

## 2. Arquitetura de Software
- **Front-end:** Streamlit Cloud.
- **Backend:** Supabase Edge Functions (utilizando a biblioteca `supabase-py`).
- **Database** Supabase PostgresSQL com Data API habilitada com RLS
- **Multi-tenancy:** Baseado em coluna `cliente_id` em todas as tabelas (Estratégia de Row-Level Security futura).
- **Sessão/Auth:** Login único compartilhado por cliente. No início do app, o usuário deve selecionar seu nome (Responsável) em um dropdown. Este nome deve ser salvo no `st.session_state` e enviado em cada movimentação.

## 3. Modelo de Dados (Supabase/Postgres)

Obs.: O Supabase PostgresSQL tem Data API para que pode ser usado direto no streamlit

[Script para criar as tabelas do projeto](../scripts/script-create-tables.sql)

exemplo de request:
import requests

url = "https://krivbykcprcvlgamrfzy.supabase.co/rest/v1/produtos"

headers = {
    "apikey": "ey...",
    "Accept": "application/json"
}

params = {
    "select": "*"
}

autorization = {
    "bearear token": "ey..."
}

response = requests.get(url, headers=headers, params=params)

print(response.status_code)
print(response.json())

exemplo de resposta:
[
    {
        "id": "5561db35-346a-4932-a6d8-655d90e3ae0c",
        "cliente_id": "b4440a38-c0d5-40c7-a0e2-8e1eaf7dcba4",
        "especie": "Eucalipto",
        "tipo_peca": "Tábua",
        "dimensoes": "2x30x300",
        "unidade_medida": "m²",
        "preco_unitario": 120.50,
        "estoque_atual": 10
    }
]


## 4. Instruções de UI/UX (Streamlit)
- **Mobile First:** Use `st.columns` com moderação. Prefira widgets que ocupem a largura total.
- **Entrada de Dados:** - Use `st.selectbox` para Espécie, Tipo e Unidade (buscando da tabela `parametros`).
    - Use `st.number_input` com `step=1.0` ou `0.01` dependendo da unidade.
- **Filtros:** Sempre filtrar todas as queries por `cliente_id`.

## 5. Fluxo de Código Sugerido
1. **Init:** Verificar se `cliente_id` e `responsavel` estão no `st.session_state`.
2. **Login:** Tela simples de senha para liberar o acesso ao tenant.
3. **Seleção de Responsável:** Dropdown obrigatório antes de liberar o menu.
4. **Dashboard:** Mostrar saldo atual (tabela `produtos`).
5. **Formulário de Movimentação:** - Seleciona Produto -> Tipo (E/S) -> Quantidade -> Salvar.
    - Ao salvar, usar um RPC no Supabase ou uma transação para atualizar `produtos.estoque_atual` e inserir em `movimentacoes`.

## 6. Restrições e Riscos
- **Offline:** O app não funciona offline. Adicionar aviso visual se a conexão falhar.
- **Concorrência:** Sempre usar a lógica de (Estoque Atual + Nova Movimentação) para evitar erros se dois funcionários lançarem ao mesmo tempo.
- **Simplicidade:** Não implementar QR Code ou fotos nesta versão.

## 7. Variáveis de Ambiente (.env / Secrets)
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `APP_PASSWORD` (Senha simples de acesso ao MVP)


---

Exemplo das Políticas RLS mínimas para o MVP:
-- SELECT: usuário só vê seus próprios registros
CREATE POLICY "select_own_rows"
ON estoque
FOR SELECT
USING (user_id = auth.uid());

-- INSERT: usuário só insere registros vinculados ao seu ID
CREATE POLICY "insert_own_rows"
ON estoque
FOR INSERT
WITH CHECK (user_id = auth.uid());

-- UPDATE: usuário só atualiza seus próprios registros
CREATE POLICY "update_own_rows"
ON estoque
FOR UPDATE
USING (user_id = auth.uid());

---

Referências reais do projeto
![Tela do Supabase com uma referência visual do esquema do banco de dados do projeto, mostrando tabelas e relacionamentos para clientes, parâmetros, produtos e movimentações.](../img/image.png)

