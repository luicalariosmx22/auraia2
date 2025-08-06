-- Crear tabla logs_webhooks_meta con todos los campos necesarios
-- Incluyendo nombre_nora para evitar errores de columna faltante

create table if not exists public.logs_webhooks_meta (
  id bigserial not null,
  tipo_objeto text not null,
  objeto_id text not null,
  campo text not null,
  valor text null,
  timestamp timestamp without time zone not null default now(),
  nombre_nora text null,
  id_cuenta_publicitaria text null,
  recibido_en timestamp without time zone null default now(),
  procesado boolean null default false,
  procesado_en timestamp with time zone null,
  constraint logs_webhooks_meta_pkey primary key (id)
) TABLESPACE pg_default;

-- Crear índices para optimizar consultas
create index IF not exists idx_logs_webhooks_meta_objeto_id on public.logs_webhooks_meta using btree (objeto_id) TABLESPACE pg_default;

create index IF not exists idx_logs_webhooks_meta_timestamp on public.logs_webhooks_meta using btree ("timestamp") TABLESPACE pg_default;

create index IF not exists idx_logs_webhooks_meta_procesado on public.logs_webhooks_meta using btree (procesado) TABLESPACE pg_default;

-- Crear trigger solo si la función existe
-- create trigger trg_auto_update_webhook_meta BEFORE INSERT on logs_webhooks_meta for EACH row
-- execute FUNCTION actualizar_info_webhook_meta ();
