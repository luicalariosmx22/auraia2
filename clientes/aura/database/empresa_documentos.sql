-- Tabla para documentos importantes ligados a una empresa
create table empresa_documentos (
    id uuid primary key default uuid_generate_v4(),
    empresa_id uuid references cliente_empresas(id) on delete cascade,
    nombre varchar(255) not null,
    url text not null,
    creado_en timestamp with time zone default now()
);
