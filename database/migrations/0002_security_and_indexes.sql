-- Explicit administrator-only policies for server-managed tables.
-- The role is read from immutable app_metadata, never user-editable metadata.
create policy knowledge_documents_admin on public.knowledge_documents for all to authenticated
using ((select auth.jwt()->'app_metadata'->>'role') = 'admin')
with check ((select auth.jwt()->'app_metadata'->>'role') = 'admin');
create policy knowledge_chunks_admin on public.knowledge_chunks for all to authenticated
using ((select auth.jwt()->'app_metadata'->>'role') = 'admin')
with check ((select auth.jwt()->'app_metadata'->>'role') = 'admin');
create policy ingestion_jobs_admin on public.document_ingestion_jobs for all to authenticated
using ((select auth.jwt()->'app_metadata'->>'role') = 'admin')
with check ((select auth.jwt()->'app_metadata'->>'role') = 'admin');
create policy evaluation_runs_admin on public.rag_evaluation_runs for all to authenticated
using ((select auth.jwt()->'app_metadata'->>'role') = 'admin')
with check ((select auth.jwt()->'app_metadata'->>'role') = 'admin');
create policy evaluations_admin on public.rag_evaluations for all to authenticated
using ((select auth.jwt()->'app_metadata'->>'role') = 'admin')
with check ((select auth.jwt()->'app_metadata'->>'role') = 'admin');
create policy audit_logs_admin_read on public.audit_logs for select to authenticated
using ((select auth.jwt()->'app_metadata'->>'role') = 'admin');
create policy citations_owner_read on public.message_citations for select to authenticated
using (exists(select 1 from public.messages m where m.id=message_id and m.owner_id=(select auth.uid())));

create index animal_allergies_animal_idx on public.animal_allergies(animal_id);
create index animal_allergies_owner_idx on public.animal_allergies(owner_id);
create index animal_conditions_animal_idx on public.animal_conditions(animal_id);
create index animal_conditions_owner_idx on public.animal_conditions(owner_id);
create index animal_weights_animal_idx on public.animal_weights(animal_id);
create index animal_weights_owner_idx on public.animal_weights(owner_id);
create index audit_logs_actor_idx on public.audit_logs(actor_id);
create index conversations_animal_idx on public.conversations(animal_id);
create index conversations_owner_idx on public.conversations(owner_id);
create index ingestion_jobs_document_idx on public.document_ingestion_jobs(document_id);
create index feedback_message_idx on public.feedback(message_id);
create index feedback_owner_idx on public.feedback(owner_id);
create index knowledge_documents_uploader_idx on public.knowledge_documents(uploaded_by);
create index lab_reports_animal_idx on public.lab_reports(animal_id);
create index lab_reports_file_idx on public.lab_reports(file_id);
create index lab_reports_owner_idx on public.lab_reports(owner_id);
create index lab_results_report_idx on public.lab_results(report_id);
create index medical_records_animal_idx on public.medical_records(animal_id);
create index medical_records_owner_idx on public.medical_records(owner_id);
create index medications_animal_idx on public.medications(animal_id);
create index medications_owner_idx on public.medications(owner_id);
create index message_citations_chunk_idx on public.message_citations(chunk_id);
create index messages_conversation_idx on public.messages(conversation_id);
create index messages_owner_idx on public.messages(owner_id);
create index evaluation_runs_starter_idx on public.rag_evaluation_runs(started_by);
create index evaluations_run_idx on public.rag_evaluations(run_id);
create index uploaded_files_animal_idx on public.uploaded_files(animal_id);
create index uploaded_files_owner_idx on public.uploaded_files(owner_id);
create index vaccinations_animal_idx on public.vaccinations(animal_id);
create index vaccinations_owner_idx on public.vaccinations(owner_id);
