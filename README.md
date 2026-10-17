# Consulta Clima

Dashboard de clima em desenvolvimento para a especialização em Engenharia de Software
da UFG. O objetivo do projeto é consultar a OpenWeatherMap e apresentar as condições
atuais e previsões em uma página web.

> **Status: trabalho em andamento.** O servidor entrega uma página com condições
> meteorológicas atuais, obtidas por uma rota da API. Previsões, busca de cidades e
> mapa ainda não estão implementados.

## Estado atual

- `app/main.py` cria o cliente OpenWeatherMap e serve os arquivos em `static/`.
- `GET /api/weather/current` consulta as condições atuais e mantém a chave no servidor.
- `app/api/routes.py` contém outras rotas planejadas, mas ainda depende de módulos
  de domínio e schemas que não foram implementados nem registrados na aplicação.
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

Crie o arquivo `.env` a partir do exemplo e preencha sua própria chave da OpenWeatherMap.
Não publique esse arquivo:

```bash
cp .env.example .env
```

No Windows, use `copy .env.example .env`. Inicie o servidor na raiz do projeto:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --env-file .env --reload
```

Abra <http://127.0.0.1:8000>. No Codespaces, encaminhe a porta `8000` pela aba
**Ports** para acessar a página.

Ao carregar a página, o navegador solicita sua localização. Se ela não estiver disponível,
o painel consulta Uberlândia como localização padrão. Cada atualização consulta o endpoint
de condições atuais da OpenWeatherMap.

## Próximos passos

1. Implementar e conectar a busca de cidades e a localização reversa.
2. Implementar as previsões diária, por hora e por minuto.
3. Adicionar o mapa de precipitação e completar os estados da interface.
4. Implementar as rotas restantes, schemas, testes e documentação do projeto.

## Segurança

Nunca inclua a chave da OpenWeatherMap em código, documentação, commits ou mensagens.
Mantenha-a apenas no arquivo `.env` local, que não deve ser enviado ao GitHub.
