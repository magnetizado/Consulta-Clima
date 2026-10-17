# Consulta Clima

Dashboard de clima em desenvolvimento para a especialização em Engenharia de Software
da UFG. O objetivo do projeto é consultar a OpenWeatherMap e apresentar as condições
atuais e previsões em uma página web.

> **Status: trabalho em andamento.** O servidor entrega uma página com condições
> meteorológicas atuais, obtidas por uma rota da API. Previsões, busca de cidades e
> mapa ainda não estão implementados.

## Estado atual

- `app/main.py` cria o cliente OpenWeatherMap e serve os arquivos em `static/`.
- `GET /api/weather/current` consulta as condições atuais para o cartão inicial.
- `GET /api/weather`, `/api/geo/search`, `/api/geo/reverse` e
  `/api/tiles/precipitation/{z}/{x}/{y}.png` estão conectadas ao cliente do provedor.
- Os módulos de domínio e schemas dão às rotas contratos de resposta consistentes,
  documentados abaixo.
- A chave da OpenWeatherMap não deve ser versionada. O arquivo `.env` é ignorado pelo
  Git; o servidor precisa dela para iniciar.

## Requisitos

- Python 3.13.5
- Git
- Uma chave válida da OpenWeatherMap, configurada localmente no arquivo `.env`.

## Executar localmente

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

Se ainda não tiver um arquivo `.env`, crie-o a partir do exemplo e preencha sua própria
chave da OpenWeatherMap. Se já existir, não o sobrescreva. Nunca publique esse arquivo:

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

## Contrato inicial da API

As rotas recebem apenas parâmetros públicos. O servidor acrescenta a chave do provedor;
ela nunca é devolvida nas respostas.

- `GET /api/weather?lat={latitude}&lon={longitude}` devolve `timezone_offset` e os blocos
  disponíveis `current`, `minutely`, `hourly`, `daily` e `alerts`. Cada bloco contém os
  registros normalizados recebidos do cliente OpenWeatherMap.
- `GET /api/geo/search?q={termo}` devolve `{"results":[...]}`. Cada cidade inclui `name`,
  `lat`, `lon`, `country` e, quando disponível, `state`.
- `GET /api/geo/reverse?lat={latitude}&lon={longitude}` devolve `{"result":...}` ou
  `{"result":null}` quando nenhuma cidade é encontrada.
- `GET /api/tiles/precipitation/{z}/{x}/{y}.png` devolve uma imagem PNG da camada de chuva.

## Próximos passos

1. Conectar a busca de cidades e a localização reversa ao frontend.
2. Mostrar as previsões diária, por hora e por minuto na interface.
3. Adicionar o mapa de precipitação e completar os estados da interface.
4. Expandir os testes do navegador e atualizar a documentação dos requisitos.

## Segurança

Nunca inclua a chave da OpenWeatherMap em código, documentação, commits ou mensagens.
Mantenha-a apenas no arquivo `.env` local, que não deve ser enviado ao GitHub.
