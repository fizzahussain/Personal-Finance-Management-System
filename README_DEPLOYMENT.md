# Deployment notes

## Vercel API

This branch contains a Vercel-compatible FastAPI entry point at `api/index.py` and Vercel configuration in `vercel.json`.

Set the following Vercel environment variable before using authentication:

```text
FINANCE_JWT_SECRET_KEY=<long-random-secret>
```

After deployment, FastAPI documentation is available at `/docs`.

## Streamlit dashboard

The Streamlit dashboard is not deployed by Vercel. Deploy it separately (for example, Streamlit Community Cloud) and set its `API_BASE_URL` environment variable to:

```text
https://<your-vercel-domain>/api/v1
```

The dashboard reads `API_BASE_URL` from the environment and falls back to the local development URL when it is not set.

## Database limitation

The application currently uses SQLite. Vercel serverless storage must not be treated as durable application storage. The deployed API is therefore suitable for deployment/testing, but before relying on it for real users or persistent financial data, migrate the storage layer to a hosted PostgreSQL database.
