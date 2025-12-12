# Cloudflare Worker Proxy

Cloudflare Worker для проксирования всех запросов на http://razr.freedynamicdns.org:5001/

## Установка

```bash
npm install
```

## Разработка

Запуск локального dev сервера:

```bash
npm run dev
```

Worker будет доступен на `http://localhost:8787`

## Деплой

Деплой в Cloudflare:

```bash
npm run deploy
```

При первом деплое вам может потребоваться войти в аккаунт Cloudflare.

## Использование

После деплоя все запросы к вашему worker URL будут проксированы на `http://razr.freedynamicdns.org:5001/`

Путь и query параметры сохраняются, например:
- `https://your-worker.workers.dev/api/test?id=1` → `http://razr.freedynamicdns.org:5001/api/test?id=1`
