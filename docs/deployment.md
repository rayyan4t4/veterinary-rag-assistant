# Deployment

## Supabase

Create a project, run `database/migrations/0001_initial.sql` in the SQL editor, confirm RLS is enabled, then create email/password and Google Auth settings. Add the frontend URL and callback URL to Auth URL configuration. Keep the service-role key on the API host only. Private storage objects use paths beginning with the authenticated user UUID.

## Render API

Create a Docker web service from this repository using `docker/api.Dockerfile`. Set `DATABASE_URL` to the Supabase pooler connection string (changing the scheme to `postgresql+asyncpg`), configure `SUPABASE_URL`, and add provider secrets. Set the health path to `/health`.

## Vercel web

Import `apps/web` as the project root. Set `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, and `NEXT_PUBLIC_API_BASE_URL` to the deployed API. Never add the service-role key to Vercel browser environment variables.
