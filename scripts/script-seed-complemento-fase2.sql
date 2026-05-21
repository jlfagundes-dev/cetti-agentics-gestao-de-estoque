-- =========================================================================
-- SEED COMPLEMENTAR - TESTE DE DADOS FASE 2
-- =========================================================================

-- 1. Inserindo Entidades de Teste (Cliente e Fornecedor)
INSERT INTO entidades (cliente_id, nome_razao, tipo_entidade, documento)
VALUES 
(
  (SELECT id FROM clientes WHERE slug = 'madeireira-exemplo'),
  'Madeiras Reflorestadas S.A.',
  'fornecedor',
  '12.345.678/0001-99'
),
(
  (SELECT id FROM clientes WHERE slug = 'madeireira-exemplo'),
  'Construtora Silva & Filhos',
  'cliente',
  '98.765.432/0001-00'
);


-- 2. Inserindo uma Movimentação Comercial de ENTRADA (Compra de Fornecedor)
-- Cenário: Comprando mais 20 unidades do produto existente (Eucalipto Tábua)
INSERT INTO movimentacoes (
    cliente_id, 
    produto_id, 
    tipo_movimentacao, 
    natureza_operacao, 
    entidade_id, 
    quantidade, 
    valor_monetario_total, 
    responsavel
)
VALUES (
  (SELECT id FROM clientes WHERE slug = 'madeireira-exemplo'),
  (SELECT id FROM produtos WHERE especie = 'Eucalipto' AND tipo_peca = 'Tábua' LIMIT 1),
  'entrada',
  'compra',
  (SELECT id FROM entidades WHERE nome_razao = 'Madeiras Reflorestadas S.A.' LIMIT 1),
  20.00,
  2410.00, -- 20 unidades * R$ 120.50 (Preço unitário)
  'José'
);


-- 3. Inserindo uma Movimentação Comercial de SAÍDA (Baixa por Venda para Cliente)
-- Cenário: Vendendo 3 unidades do mesmo produto para a Construtora
INSERT INTO movimentacoes (
    cliente_id, 
    produto_id, 
    tipo_movimentacao, 
    natureza_operacao, 
    entidade_id, 
    quantidade, 
    valor_monetario_total, 
    responsavel
)
VALUES (
  (SELECT id FROM clientes WHERE slug = 'madeireira-exemplo'),
  (SELECT id FROM produtos WHERE especie = 'Eucalipto' AND tipo_peca = 'Tábua' LIMIT 1),
  'saida',
  'venda',
  (SELECT id FROM entidades WHERE nome_razao = 'Construtora Silva & Filhos' LIMIT 1),
  3.00,
  361.50, -- 3 unidades * R$ 120.50 (Preço unitário)
  'Maria'
);


-- 4. Atualizando o estoque_atual do produto do Seed para refletir as novas movimentações
-- Começou com 10 (Fase 1) + 20 (Compra) - 3 (Venda) = 27
UPDATE produtos 
SET estoque_atual = 27
WHERE especie = 'Eucalipto' AND tipo_peca = 'Tábua' 
AND cliente_id = (SELECT id FROM clientes WHERE slug = 'madeireira-exemplo');