drop policy knowledge_documents_admin on public.knowledge_documents;
drop policy knowledge_chunks_admin on public.knowledge_chunks;
drop policy ingestion_jobs_admin on public.document_ingestion_jobs;
drop policy evaluation_runs_admin on public.rag_evaluation_runs;
drop policy evaluations_admin on public.rag_evaluations;
drop policy audit_logs_admin_read on public.audit_logs;

create policy knowledge_documents_admin on public.knowledge_documents for all to authenticated
using (((select auth.jwt())->'app_metadata'->>'role') = 'admin')
with check (((select auth.jwt())->'app_metadata'->>'role') = 'admin');
create policy knowledge_chunks_admin on public.knowledge_chunks for all to authenticated
using (((select auth.jwt())->'app_metadata'->>'role') = 'admin')
with check (((select auth.jwt())->'app_metadata'->>'role') = 'admin');
create policy ingestion_jobs_admin on public.document_ingestion_jobs for all to authenticated
using (((select auth.jwt())->'app_metadata'->>'role') = 'admin')
with check (((select auth.jwt())->'app_metadata'->>'role') = 'admin');
create policy evaluation_runs_admin on public.rag_evaluation_runs for all to authenticated
using (((select auth.jwt())->'app_metadata'->>'role') = 'admin')
with check (((select auth.jwt())->'app_metadata'->>'role') = 'admin');
create policy evaluations_admin on public.rag_evaluations for all to authenticated
using (((select auth.jwt())->'app_metadata'->>'role') = 'admin')
with check (((select auth.jwt())->'app_metadata'->>'role') = 'admin');
create policy audit_logs_admin_read on public.audit_logs for select to authenticated
using (((select auth.jwt())->'app_metadata'->>'role') = 'admin');
