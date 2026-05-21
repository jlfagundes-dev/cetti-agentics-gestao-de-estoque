# Cursor/Copilot Rules - SaaS Estoque Madeireira (FASE 2)

Este documento serve como instrução de contexto obrigatória para o desenvolvimento da FASE 2 do SaaS de controle de estoque. Siga rigorosamente estas definições para manter a consistência do projeto.

## 1. Visão Geral (Fase 2)
- **Objetivo:** Expandir o MVP (Fase 1) adicionando um fluxo comercial completo de entrada (Fornecedores) e saída (Vendas/Clientes), mantendo a arquitetura leve e mobile-first no Streamlit.
- **Stack:** Python (Streamlit), Supabase (PostgreSQL via REST/Data API).
- **Abordagem Técnica:** Todo e qualquer dado persistido ou consultado DEVE estar estritamente amarrado ao `cliente_id` ativo no `st.session_state`.

## 2. Modelo de Dados Expandido (Supabase/Postgres)

Para evitar inflação de tabelas desnecessárias, Clientes e Fornecedores compartilham a tabela `entidades`, diferenciados pela coluna `tipo_entidade`.

### Tabela: `entidades` (Nova)
- `id`: uuid (primary key)
- `cliente_id`: uuid (foreign key para o tenant)
- `nome_razao`: text (Nome do Cliente ou Fornecedor)
- `tipo_entidade`: text ('cliente' ou 'fornecedor')
- `documento`: text (CPF/CNPJ opcional)
- `telefone`: text (opcional)
- `email`: text (opcional)
- `created_at`: timestamp with time zone

### Tabela: `movimentacoes` (Atualizada para a Fase 2)
- `id`: uuid (primary key)
- `cliente_id`: uuid (foreign key)
- `produto_id`: uuid (foreign key)
- `tipo_movimentacao`: text ('entrada' ou 'saida')
- `natureza_operacao`: text ('compra', 'venda', 'ajuste_inventario') -> Nova coluna explicativa
- `entidade_id`: uuid (foreign key para `entidades.id`, nullable para ajustes manuais) -> Nova coluna
- `quantidade`: numeric
- `valor_monetario_total`: numeric -> Nova coluna (Qtd * Preço aplicado no momento da transação)
- `responsavel`: text (nome do funcionário vindo do session_state)
- `created_at`: timestamp with time zone

### Tabelas Existentes da Fase 1 (Manter estrutura):
- `clientes` (Tenants do SaaS)
- `parametros` (Domínios de espécie, tipo de peça e unidade)
- `produtos` (`id`, `cliente_id`, `especie`, `tipo_peca`, `dimensoes`, `unidade_medida`, `preco_unitario`, `estoque_atual`)

## 3. Regras de Negócio e Fluxos Clínicos da Fase 2

### Fluxo A: Cadastro de Entidades (Clientes / Fornecedores)
- Interface simplificada de formulário para cadastrar novos Clientes ou Fornecedores.
- **Validação de Entrada:** Bloquear cadastros sem nome ou sem o `tipo_entidade` explicitamente definido.

### Fluxo B: Entrada de Estoque (Recebimento de Fornecedor / Compra)
- **Operação:** `tipo_movimentacao` = 'entrada', `natureza_operacao` = 'compra'.
- O dropdown de origem deve listar apenas registros de `entidades` onde `tipo_entidade` == 'fornecedor' AND `cliente_id` == `st.session_state.cliente_id`.
- Incrementa dinamicamente a coluna `estoque_atual` na tabela `produtos`.

### Fluxo C: Saída de Estoque (Baixa por Venda)
- **Operação:** `tipo_movimentacao` = 'saida', `natureza_operacao` = 'venda'.
- O dropdown de destino deve listar apenas registros de `entidades` onde `tipo_entidade` == 'cliente' AND `cliente_id` == `st.session_state.cliente_id`.
- **Validação Crítica:** Impedir a venda se a `quantidade` inserida for maior que o `estoque_atual` do produto escolhido. Mostrar erro amigável na tela do celular.
- Decrementa dinamicamente a coluna `estoque_atual` na tabela `produtos`.

## 4. Diretrizes Rígidas para Geração de Código (Prompt Guardrails)

- **Filtro Injetado:** NUNCA realize um `rest_get`, `rest_post` ou `rest_patch` sem passar o parâmetro de query correspondente ao `cliente_id` capturado do `st.session_state.cliente_id`. 
- **Exemplo de GET filtrado para Entidades (Clientes/Fornecedores):**
```python
params = {
    "select": "*",
    "cliente_id": f"eq.{st.session_state.cliente_id}",
    "tipo_entidade": f"eq.cliente"
}
- Interface Limpa: Como o uso é mobile (pátio de madeireira), os formulários de Venda ou Recebimento devem usar componentes empilhados verticalmente. Evite colocar colunas lado a lado no celular para prevenir cortes visuais.
- Tratamento de Sessão: Se o st.session_state.step mudar ou o app reiniciar, garanta que os estados de cliente_id e responsavel persistam até que um logout explícito ocorra.