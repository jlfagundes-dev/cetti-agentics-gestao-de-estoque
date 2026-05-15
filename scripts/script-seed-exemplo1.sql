-- CLIENTES
insert into clientes (nome_empresa, slug)
values ('Madeireira Exemplo', 'madeireira-exemplo');

-- Pegamos o id do cliente recém-criado
-- (em Supabase você pode usar RETURNING, mas aqui vou usar subselects)

-- PARAMETROS
insert into parametros (cliente_id, tipo, valor)
values (
  (select id from clientes where slug = 'madeireira-exemplo'),
  'unidade_medida',
  'm²'
);

-- PRODUTOS
insert into produtos (cliente_id, especie, tipo_peca, dimensoes, unidade_medida, preco_unitario, estoque_atual)
values (
  (select id from clientes where slug = 'madeireira-exemplo'),
  'Eucalipto',
  'Tábua',
  '2x30x300',
  'm²',
  120.50,
  10
);

-- MOVIMENTACOES
insert into movimentacoes (cliente_id, produto_id, tipo_movimentacao, quantidade, responsavel)
values (
  (select id from clientes where slug = 'madeireira-exemplo'),
  (select id from produtos where especie = 'Eucalipto' and tipo_peca = 'Tábua'),
  'Entrada',
  5,
  'José'
);
