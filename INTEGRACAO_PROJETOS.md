# Guia de Integração dos Projetos Existentes

Este documento explica como integrar seus projetos existentes no portfólio Django.

## Estrutura Criada

O portfólio foi configurado com os seguintes apps para seus projetos:

e.g.
- `sindsebsystem/` - Para o projeto SindsebSystem


## Como Integrar Cada Projeto

### 1. Para Projetos Django Existentes (ex: SindsebSystem)

**Passo 1:** Copie os arquivos do seu projeto existente
```bash
# Copie os models
cp /caminho/seu_projeto/models.py sindsebsystem/models.py

# Copie as views
cp /caminho/seu_projeto/views.py sindsebsystem/views.py

# Copie os templates
cp -r /caminho/seu_projeto/templates/* templates/sindsebsystem/

# Copie arquivos estáticos
cp -r /caminho/seu_projeto/static/* static/
```

**Passo 2:** Atualize as URLs
- Edite `sindsebsystem/urls.py` com as URLs do seu projeto
- As URLs já estão configuradas em `/projetos/sindseb/`

**Passo 3:** Execute migrações se necessário
```bash
python manage.py makemigrations sindsebsystem
python manage.py migrate
```

### 2. Para Projetos React/Frontend (ex: E-commerce)

**Opção A - Build estático:**
```bash
# Faça o build do seu projeto React
npm run build

# Copie os arquivos para o Django
cp -r build/* static/ecommerce/

# Crie um template que carrega o build
```

**Opção B - Iframe:**
- Mantenha seu projeto rodando em porta separada
- Use iframe no template Django para exibir

### 3. Para Projetos Mobile (ex: TaQuanto)

- Crie páginas de demonstração (já feito para TaQuanto)
- Mostre screenshots, funcionalidades e código
- Link para repositório GitHub

### 4. Para Projetos CS50W

- Cada projeto pode ser um subdiretório
- Configure URLs como `/projetos/cs50w/projeto1/`
- Integre como projetos Django separados

## URLs Configuradas

Seus projetos estarão acessíveis em:

- `/projetos/taquanto/` - TaQuanto
- `/projetos/sindseb/` - SindsebSystem  
- `/projetos/cs50w/` - Projetos CS50W
- `/projetos/ecommerce/` - E-commerce
- `/projetos/finance-tracker/` - Finance Tracker

## Atualizando o Portfólio Principal

Para que os projetos apareçam na página inicial, atualize:

1. **Banco de dados:** Adicione os projetos via admin Django
2. **Templates:** Os links já estão configurados nos templates

## Comandos Úteis

```bash
# Rodar o servidor
python manage.py runserver 0.0.0.0:8000

# Criar superusuário para admin
python manage.py createsuperuser

# Fazer migrações
python manage.py makemigrations
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic
```

## Estrutura de Arquivos

```
portfolio_cleilton/
├── core/                 # App principal do portfólio
├── projects/            # App para gerenciar lista de projetos
├── contact/             # App de contato
├── taquanto/           # Seu projeto TaQuanto
├── sindsebsystem/      # Seu projeto SindsebSystem
├── cs50w_projects/     # Seus projetos CS50W
├── ecommerce/          # Seu projeto E-commerce
├── finance_tracker/    # Seu projeto Finance Tracker
├── templates/          # Templates globais
├── static/             # Arquivos estáticos globais
└── media/              # Uploads de arquivos
```

## Próximos Passos

1. Copie seus projetos existentes para os apps correspondentes
2. Atualize as URLs conforme necessário
3. Teste cada projeto individualmente
4. Adicione os projetos no admin Django
5. Personalize os templates conforme necessário

## Suporte

Se precisar de ajuda com a integração de algum projeto específico, consulte a documentação do Django ou entre em contato.

