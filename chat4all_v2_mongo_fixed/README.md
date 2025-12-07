# Chat4All v2 – Mongo Edition (POC)

Este repositório contém uma prova de conceito da plataforma **Chat4All v2** usando:

- API em **FastAPI**
- Persistência de mensagens em **MongoDB**
- Fila de eventos com **Kafka**
- Armazenamento de arquivos em **MinIO (S3‑compatible)**
- Worker de roteamento que consome mensagens do Kafka e entrega via *connectors* mockados

> Banco distribuído para mensagens: MongoDB, conforme requisitos do enunciado (substituindo Cassandra).

## Serviços principais

- `api` – API REST (FastAPI)
  - Autenticação via token estático de demo.
  - Endpoints:
    - `POST /auth/token`
    - `POST /v1/conversations`
    - `GET  /v1/conversations/{conversation_id}/messages`
    - `POST /v1/messages`
    - `POST /v1/files/initiate`
    - `POST /v1/files/complete`
    - `POST /v1/webhooks/delivery` (mock)
- `router` – worker que:
  - Consome eventos `chat4all.messages` no Kafka
  - Atualiza o status da mensagem no MongoDB
  - Chama *connectors* mockados (WhatsApp / Instagram)
- `mongo` – banco de dados de mensagens
- `kafka` + `zookeeper` – backbone de eventos
- `minio` – armazenamento de arquivos
- `mongo-express` – UI web simples para inspecionar o MongoDB (opcional)

## Como executar

Pré‑requisitos:

- Docker
- Docker Compose v2

Passos:

```bash
cd chat4all_v2_mongo
docker compose up --build
```

A API ficará disponível em: http://localhost:8080/docs

> A ordem causal por conversa é garantida no nível de aplicação por um `sequence` incremental por `conversation_id`.

## Fluxo básico de teste

1. Obter token (demo):

```bash
curl -X POST http://localhost:8080/auth/token   -H "Content-Type: application/json"   -d '{"client_id":"demo","client_secret":"demo"}'
```

2. Criar conversa:

```bash
curl -X POST http://localhost:8080/v1/conversations   -H "Authorization: Bearer <access_token>"   -H "Content-Type: application/json"   -d '{
    "type":"private",
    "members":["userA","userB"],
    "metadata":{}
  }'
```

3. Enviar mensagem:

```bash
curl -X POST http://localhost:8080/v1/messages   -H "Authorization: Bearer <access_token>"   -H "Content-Type: application/json"   -d '{
    "conversation_id":"<id_da_conversa>",
    "from_user":"userA",
    "to":["userB"],
    "channels":["whatsapp","instagram"],
    "payload":{"type":"text","text":"Olá do Chat4All!"}
  }'
```

4. Ver mensagens:

```bash
curl -X GET "http://localhost:8080/v1/conversations/<id_da_conversa>/messages"   -H "Authorization: Bearer <access_token>"
```

5. O worker `router` irá consumir a mensagem do Kafka, simular a entrega via *connectors* mockados e atualizar o status para `DELIVERED`.

## Observações

- Este projeto é uma **POC didática** – não é voltado a produção.
- Para integração com canais reais (ex.: Telegram), substitua os *connectors* mockados por implementações reais.
- O código foi reestruturado para evitar dependências inválidas e usar **MongoDB** em todos os pontos de persistência.
