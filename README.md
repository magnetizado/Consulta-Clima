# Consulta Clima

Dashboard de clima em desenvolvimento para a especialização em Engenharia de Software
da UFG. O objetivo do projeto é consultar a OpenWeatherMap e apresentar as condições
atuais e previsões em uma página web.

> **Status: trabalho em andamento.** Esta cópia contém a estrutura inicial do servidor
> FastAPI e uma página estática de boas-vindas. A consulta de clima, as rotas da API e
> as funcionalidades do dashboard ainda não estão conectadas.

## Estado atual

- `app/main.py` serve `static/index.html` e os arquivos em `static/`.
- `app/api/routes.py` e `app/clients/openweather.py` contêm partes iniciais da API,
  mas as rotas ainda não são registradas na aplicação.
- Os módulos de domínio e schemas esperados por `app/api/routes.py` ainda precisam
  ser implementados.
- A chave da OpenWeatherMap não deve ser versionada. O arquivo `.env` é ignorado pelo
  Git; use `.env.example` como referência ao configurar a integração futuramente.

## Requisitos

- Python 3.13.5
- Git
- Uma chave da OpenWeatherMap será necessária quando a integração com o provedor
  estiver implementada.

## Executar a página inicial

Crie e ative o ambiente Python e instale as dependências:

```bash
conda env create -f environment.yml
conda activate openweather-dashboard
```

Ou, com Python 3.13.5 e `venv`:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

Inicie o servidor na raiz do projeto:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Abra <http://127.0.0.1:8000>. No Codespaces, encaminhe a porta `8000` pela aba
**Ports** para acessar a página.

## Próximos passos

1. Implementar os schemas e as regras de domínio usados pelas rotas.
2. Integrar as rotas da API ao ciclo de vida da aplicação.
3. Construir o dashboard no frontend e conectar os dados meteorológicos.
4. Adicionar testes e documentar os requisitos e as decisões do projeto.

## Segurança

Nunca inclua a chave da OpenWeatherMap em código, documentação, commits ou mensagens.
Mantenha-a apenas no arquivo `.env` local, que não deve ser enviado ao GitHub.
