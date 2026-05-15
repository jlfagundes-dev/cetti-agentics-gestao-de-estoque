# Cetti - Gestão de Estoque (Streamlit + Supabase)

Este repositório contém um exemplo mínimo de app Streamlit que usa Supabase (Postgres) para armazenar produtos.

## Arquivos principais
- [app.py](app.py) - aplicação Streamlit
- [supabase_client.py](supabase_client.py) - helper para criar o cliente Supabase
- [requirements.txt](requirements.txt)

## Como rodar localmente

1. Criar um projeto no Supabase (ver seção abaixo).
2. Copiar `SUPABASE_URL` e `SUPABASE_KEY` (anon/public ou service role conforme necessidade).
3. Exportar variáveis de ambiente localmente ou criar um arquivo `.env` com as chaves:

```
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_KEY=eyJ....
```

4. Instalar dependências:

```bash
python -m pip install -r requirements.txt
```

5. Executar:

```bash
streamlit run app.py
```

## Configurar o Supabase (passos mínimos)

1. Crie um novo projeto em https://app.supabase.com
2. Abra SQL Editor e execute o SQL abaixo para criar a tabela `products`:

```sql
create table if not exists products (
  id serial primary key,
  name text not null,
  quantity integer not null default 0,
  price numeric(10,2) default 0
);
```

3. (Opcional) Ative Row Level Security e crie políticas adequadas. Para começar rápido, deixe RLS desabilitado.
4. Obtenha `SUPABASE_URL` (Settings → API) e `SUPABASE_KEY` (Settings → API → Anon/Public key or Service Role).

## Deploy no Streamlit Cloud

1. Faça push do repositório para o GitHub.
2. No https://share.streamlit.io, conecte sua conta GitHub e crie um novo app apontando para este repo e branch.
3. Nas configurações do app (Secrets), adicione `SUPABASE_URL` e `SUPABASE_KEY` como segredos.
4. Configure o comando de execução (padrão) `streamlit run app.py` se necessário.

## Segurança

- Nunca coloque a `service_role` key em clientes públicos. Use-a apenas em backends seguros.
- Para permitir que clientes façam updates diretos, crie políticas RLS específicas que limitem acessos.

## Problemas comuns

- Se a tabela não aparece, confira se você executou o SQL no projeto correto.
- Em caso de erro 401/403, valide as chaves e o URL.

---

Feito com carinho — se quiser, eu posso: executar testes locais, adicionar CI/CD, ou expandir o CRUD com autenticação.
