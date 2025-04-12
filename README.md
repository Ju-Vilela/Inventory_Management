# Inventory_Management
PI Inventory Management

## 🚀 Configuração do Projeto

Este projeto utiliza o **Supabase** como banco de dados online e foi desenvolvido com `Django` + `Python`. Para rodar localmente, siga os passos abaixo:

---

### 📦 Setup do Banco de Dados [ ]

Este projeto usa [Supabase](https://supabase.com) para armazenar os dados.

- Crie um projeto no Supabase.
- No arquivo `.env.example`, adicione suas chaves conforme o exemplo enviado e renomeie para `.env`.
```bash
cp .env.example .env
````

> 🔒 Essas informações são sensíveis! Nunca suba sua `.env` pro GitHub.

---

### 🛠️ Inicializando o Banco de Dados [ ]

Depois de configurar suas variáveis de ambiente (ver `.env.example`), rode os comandos abaixo para criar as tabelas automaticamente no Supabase:

```bash
python manage.py makemigrations
python manage.py migrate
```

Importe os dados iniciais da planilha `DadosIniciais.xlsx`.

Pra isso, você vai precisar da biblioteca openpyxl. 
_Se ainda não tem instalada:_
```bash
pip install openpyxl

```

Se você já tem basta rodar:
```bash
python manage.py shell
exec(open('stock/importa_dados.py').read())
```

---

### 🧪 3. Rodando o Projeto [ ]

Depois de configurar as variáveis e importar os dados:

```bash
pip install -r requirements.txt
```

# Rode o servidor
```bash
python manage.py runserver
```