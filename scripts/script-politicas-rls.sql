-- Políticas de RLS porque estou usando chave anon do supabase

-- Conceder privilégios básicos ao papel anon
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO anon;

-- Garantir que futuras tabelas também recebam privilégios
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO anon;

-- CLIENTES
CREATE POLICY "select_own_clientes"
ON clientes
FOR SELECT
USING (id = auth.uid());

CREATE POLICY "insert_own_clientes"
ON clientes
FOR INSERT
WITH CHECK (id = auth.uid());

CREATE POLICY "update_own_clientes"
ON clientes
FOR UPDATE
USING (id = auth.uid());

-- PARAMETROS
CREATE POLICY "select_own_parametros"
ON parametros
FOR SELECT
USING (client_id = auth.uid());

CREATE POLICY "insert_own_parametros"
ON parametros
FOR INSERT
WITH CHECK (client_id = auth.uid());

CREATE POLICY "update_own_parametros"
ON parametros
FOR UPDATE
USING (client_id = auth.uid());

-- PRODUTOS
CREATE POLICY "select_own_produtos"
ON produtos
FOR SELECT
USING (client_id = auth.uid());

CREATE POLICY "insert_own_produtos"
ON produtos
FOR INSERT
WITH CHECK (client_id = auth.uid());

CREATE POLICY "update_own_produtos"
ON produtos
FOR UPDATE
USING (client_id = auth.uid());

-- MOVIMENTACOES
CREATE POLICY "select_own_movimentacoes"
ON movimentacoes
FOR SELECT
USING (client_id = auth.uid());

CREATE POLICY "insert_own_movimentacoes"
ON movimentacoes
FOR INSERT
WITH CHECK (client_id = auth.uid());

CREATE POLICY "update_own_movimentacoes"
ON movimentacoes
FOR UPDATE
USING (client_id = auth.uid());
