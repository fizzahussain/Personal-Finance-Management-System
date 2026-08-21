# Deployment notes

## Vercel API

This branch adds a Vercel-compatible FastAPI entry point at `api/index.py` and Vercel configuration in `vercel.json`.

Set the following environment variable in Vercel:

```text
FINANCE_JWT_SECRET_KEY=<long-random-secret>
```

After deployment, the FastAPI documentation is available at `/docs`.

## Streamlit dashboard

The Streamlit dashboard should be deployed separately (for example, Streamlit Community Cloud). Set its `API_BASE_URL` secret/environment variable to:

```text
https://<your-vercel-domain>/api/v1
```

The dashboard now reads `API_BASE_URL` from the environment and falls back to the local development URL when it is not set.

## Database limitation

The application currently uses SQLite. Vercel serverless storage should not be treated as durable application storage. For a persistent public deployment, migrate the API storage layer to a hosted PostgreSQL database before relying on the deployed service for real user data.
