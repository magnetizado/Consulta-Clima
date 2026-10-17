# Consulta Clima

Dashboard de clima em desenvolvimento para a especialização em Engenharia de Software
da UFG. O objetivo do projeto é consultar a OpenWeatherMap e apresentar as condições
atuais e previsões em uma página web.

> **Status: trabalho em andamento.** O painel mostra as condições atuais, permite
> buscar cidades e apresenta previsões diária, horária e por minuto. O mapa ainda
> não está implementado.

## Estado atual

- `app/main.py` cria o cliente OpenWeatherMap e serve os arquivos em `static/`.
- `GET /api/weather/current` oferece uma resposta somente com as condições atuais.
- `GET /api/weather`, `/api/geo/search`, `/api/geo/reverse` e
  `/api/tiles/precipitation/{z}/{x}/{y}.png` estão conectadas ao cliente do provedor.
- O painel busca as condições atuais e os blocos de previsão em `GET /api/weather`.
- O painel usa a geolocalização do navegador e permite pesquisar e selecionar uma cidade.
- O painel apresenta os dias disponíveis, as próximas 24 horas e a precipitação por minuto.
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

Ao carregar a página, o navegador solicita sua localização e o painel tenta identificar
o nome da cidade. Se a localização não estiver disponível, consulta Uberlândia como padrão.
Use **Consultar outra cidade** para buscar e selecionar um resultado. Cada atualização
consulta o clima atual e as previsões. A OpenWeatherMap pode receber até cinco chamadas
por atualização, mais uma para cada alerta de clima retornado; isso pode consumir a cota
da sua conta.

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

1. Adicionar o mapa de precipitação e completar os detalhes das condições atuais.
2. Expandir os testes do navegador e atualizar a documentação dos requisitos.

## Segurança

Nunca inclua a chave da OpenWeatherMap em código, documentação, commits ou mensagens.
Mantenha-a apenas no arquivo `.env` local, que não deve ser enviado ao GitHub.
