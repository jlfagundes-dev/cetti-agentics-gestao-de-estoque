-- Tenants
create table if not exists clientes (
	id uuid primary key default gen_random_uuid(),
	nome_empresa text not null,
	slug text not null unique
);

-- Domínios
create table if not exists parametros (
	id uuid primary key default gen_random_uuid(),
	client_id uuid not null references clientes(id),
	tipo text not null, -- 'especie' | 'tipo_peca' | 'unidade_medida'
	valor text not null
);

-- Produtos
create table if not exists produtos (
	id uuid primary key default gen_random_uuid(),
	client_id uuid not null references clientes(id),
	especie text not null,
	tipo_peca text not null,
	dimensoes text,
	unidade_medida text not null,
	preco_unitario numeric,
	estoque_atual numeric not null default 0
);

-- Movimentações
create table if not exists movimentacoes (
	id uuid primary key default gen_random_uuid(),
	client_id uuid not null references clientes(id),
	produto_id uuid not null references produtos(id),
	tipo_movimentacao text not null, -- 'Entrada' | 'Saída'
	quantidade numeric not null,
	responsavel text not null,
	created_at timestamptz not null default now()
);

create index on parametros (client_id, tipo);
create index on produtos (client_id);
create index on movimentacoes (client_id, produto_id, created_at desc);,

-- pgcrypto para conseguir usar gen_random_uuid()
create extension if not exists "pgcrypto";
