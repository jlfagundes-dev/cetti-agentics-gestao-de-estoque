-- =========================================================================
-- SCRIPT COMPLEMENTAR - FASE 2 (CLIENTES, FORNECEDORES E FLUXO COMERCIAL)
-- =========================================================================

-- 1. Criação da tabela unificada de Entidades (Clientes e Fornecedores do Tenant)
CREATE TABLE IF NOT EXISTS entidades (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id uuid NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    nome_razao text NOT NULL,
    tipo_entidade text NOT NULL, -- 'cliente' | 'fornecedor'
    documento text, -- CPF/CNPJ opcional para o MVP
    created_at timestamptz NOT NULL DEFAULT now(),
    
    -- Garante que o tipo de entidade inserido seja apenas um dos mapeados
    CONSTRAINT chk_tipo_entidade CHECK (tipo_entidade IN ('cliente', 'fornecedor'))
);

-- 2. Atualização da tabela de Movimentações para suportar a inteligência de negócios
-- Adiciona coluna de natureza da operação (Compra, Venda ou Ajuste)
ALTER TABLE movimentacoes 
ADD COLUMN IF NOT EXISTS natureza_operacao text NOT NULL DEFAULT 'ajuste_inventario';

-- Adiciona a constraint de validação para as naturezas aceitas
ALTER TABLE movimentacoes 
ADD CONSTRAINT chk_natureza_operacao CHECK (natureza_operacao IN ('compra', 'venda', 'ajuste_inventario'));

-- Adiciona o vínculo opcional (nullable) com a tabela de entidades (útil para compras/vendas)
ALTER TABLE movimentacoes 
ADD COLUMN IF NOT EXISTS entidade_id uuid REFERENCES entidades(id) ON DELETE RESTRICT;

-- Adiciona coluna de valor monetário total do lote/operação para relatórios de vendas futuros
ALTER TABLE movimentacoes 
ADD COLUMN IF NOT EXISTS valor_monetario_total numeric DEFAULT 0.0;

-- 3. Otimização de Performance (Índices para a Fase 2)
-- Agiliza a listagem de clientes/fornecedores filtrados por tenant
CREATE INDEX IF NOT EXISTS idx_entidades_cliente_tipo ON entidades (cliente_id, tipo_entidade);

-- Agiliza buscas de histórico de vendas/compras por parceiro comercial
CREATE INDEX IF NOT EXISTS idx_movimentacoes_entidade ON movimentacoes (entidade_id);

-- 4. Inserção de Parâmetros Iniciais de Unidades (Opcional - Apenas se ainda não existirem no seu banco)
-- Nota: Como você citou m², metro linear e peças, certifique-se de que o app consome esses tipos.