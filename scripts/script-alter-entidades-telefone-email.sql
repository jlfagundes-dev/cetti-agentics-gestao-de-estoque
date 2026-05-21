-- =========================================================================
-- AJUSTE FASE 2 - ADIÇÃO DE TELEFONE E EMAIL EM ENTIDADES
-- =========================================================================

-- Adiciona os campos de contato na tabela de entidades de forma opcional (nullable)
ALTER TABLE entidades 
ADD COLUMN IF NOT EXISTS telefone text,
ADD COLUMN IF NOT EXISTS email text;

-- Otimização: Criando um índice para buscas rápidas por e-mail dentro do tenant (útil se no futuro quiser evitar duplicados ou buscar por e-mail)
CREATE INDEX IF NOT EXISTS idx_entidades_email ON entidades (cliente_id, email);