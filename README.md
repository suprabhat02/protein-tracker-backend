# Backend Repository

## Stack

- FastAPI
- Python 3.11+
- MongoDB + Motor
- Pydantic v2
- JWT + secure cookies + refresh rotation

## Folder Structure

```text
backend/
├─ app/
│  ├─ api/
│  │  └─ v1/endpoints/
│  │     ├─ auth_router.py
│  │     ├─ dashboard_router.py
│  │     ├─ health_router.py
│  │     └─ user_router.py
│  ├─ config/
│  │  └─ routes.py
│  ├─ controllers/
│  │  ├─ auth_controller.py
│  │  ├─ dashboard_controller.py
│  │  └─ user_controller.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ exceptions.py
│  │  ├─ logging.py
│  │  ├─ middleware.py
│  │  ├─ rate_limit.py
│  │  ├─ responses.py
│  │  └─ security.py
│  ├─ db/
│  │  ├─ indexes.py
│  │  └─ mongo.py
│  ├─ dependencies/
│  │  ├─ auth.py
│  │  ├─ container.py
│  │  └─ request_context.py
│  ├─ models/
│  │  ├─ audit_log.py
│  │  ├─ food_log.py
│  │  ├─ session.py
│  │  └─ user.py
│  ├─ repositories/
│  │  ├─ audit_repository.py
│  │  ├─ food_log_repository.py
│  │  ├─ session_repository.py
│  │  └─ user_repository.py
│  ├─ schemas/
│  │  ├─ auth.py
│  │  ├─ common.py
│  │  ├─ dashboard.py
│  │  ├─ food_log.py
│  │  └─ user.py
│  ├─ services/
│  │  ├─ audit_service.py
│  │  ├─ auth_service.py
│  │  ├─ dashboard_service.py
│  │  ├─ food_log_service.py
│  │  ├─ token_service.py
│  │  └─ user_service.py
│  ├─ utils/
│  │  └─ hashids.py
│  └─ main.py
├─ .env.example
├─ docker-compose.yml
├─ Dockerfile
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

## Environment Setup

1. Copy `.env.example` to `.env`
2. Configure MongoDB URI and secrets
3. Set `GOOGLE_CLIENT_ID` from Google Cloud OAuth config

## Run Instructions

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Build Instructions

```bash
docker build -t protein-backend .
```

## API Contract

- Prefix: `/api/v1`
- Envelope success:

```json
{ "success": true, "data": {}, "meta": null }
```

- Envelope error:

```json
{
  "success": false,
  "error": { "code": "...", "message": "...", "details": {} }
}
```

- Pagination pattern: `?page=1&page_size=20` + `meta`

## Production Deployment Notes

- Stateless app instances behind load balancer
- MongoDB Atlas cluster with indexed collections
- Cookie security via `COOKIE_SECURE=true` in production
- Strict CORS via single or allowlisted origins
- Horizontal scaling via additional FastAPI replicas
- Container deployment through Kubernetes, ECS, or App Service

## Security Controls Included

- httpOnly access + refresh cookies
- refresh token rotation + replay detection
- CSRF double-submit cookie strategy
- strict CORS and secure headers middleware
- payload size limit middleware
- endpoint rate limits (`slowapi`)
- validation through Pydantic request schemas
- audit logging to `audit_logs`
- hashed public user identifiers (`Hashids`)

## MongoDB Collections and Indexes

### users

- `uniq_email` unique index on `email`
- `uniq_provider_sub` unique compound index on (`provider`, `provider_sub`)
- `uniq_user_public_id` unique index on `public_id`

### sessions

- `uniq_session_id` unique index on `session_id`
- `idx_user_sessions` compound index on (`user_id`, `created_at desc`)
- `ttl_sessions` TTL index on `expires_at`

### audit_logs

- `idx_user_audit` compound index on (`user_id`, `created_at desc`)
- `idx_event_audit` compound index on (`event`, `created_at desc`)

### food_logs

- `idx_user_log_date` compound index on (`user_id`, `log_date desc`)
- `idx_user_food_created` compound index on (`user_id`, `created_at desc`)

## Performance and Sharding Readiness

- Session TTL keeps auth storage bounded
- Query patterns are user-scoped for partition locality
- Preferred shard keys for future sharding:
  - `food_logs`: `{ user_id: 1, log_date: 1 }`
  - `sessions`: `{ user_id: 1, created_at: 1 }`
  - `audit_logs`: `{ user_id: 1, created_at: 1 }`
- Service/repository boundaries allow replacing Mongo repos with service-specific stores during microservice migration
