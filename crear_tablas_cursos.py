#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para crear las tablas necesarias para el módulo de CURSOS
"""

from clientes.aura.utils.supabase_client import supabase

def crear_tablas_cursos():
    """Crear las tablas necesarias para el módulo de cursos"""
    
    try:
        print("🔧 Creando tablas para el módulo de CURSOS...")
        
        # 1. Tabla de cursos
        sql_cursos = """
        CREATE TABLE IF NOT EXISTS cursos (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            nombre_nora TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            categoria TEXT,
            nivel TEXT,
            modalidad TEXT,
            precio DECIMAL(10,2),
            precio_pronto_pago DECIMAL(10,2),
            duracion_horas INTEGER,
            instructor TEXT,
            fecha_inicio DATE,
            fecha_fin DATE,
            horario_lunes TEXT,
            horario_martes TEXT,
            horario_miercoles TEXT,
            horario_jueves TEXT,
            horario_viernes TEXT,
            horario_sabado TEXT,
            horario_domingo TEXT,
            direccion TEXT,
            google_maps_link TEXT,
            contenido_detalle TEXT,
            objetivos TEXT,
            requisitos TEXT,
            max_estudiantes INTEGER DEFAULT 50,
            estudiantes_inscritos INTEGER DEFAULT 0,
            activo BOOLEAN DEFAULT true,
            fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # 2. Tabla de estudiantes
        sql_estudiantes = """
        CREATE TABLE IF NOT EXISTS estudiantes (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            nombre_nora TEXT NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT NOT NULL,
            telefono TEXT,
            fecha_nacimiento DATE,
            nivel_educativo TEXT,
            experiencia_previa TEXT,
            proyecto_empresa TEXT,
            red_social TEXT,
            profesion_ocupacion TEXT,
            activo BOOLEAN DEFAULT true,
            fecha_registro TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(email, nombre_nora)
        );
        """
        
        # 3. Tabla de inscripciones a cursos
        sql_inscripciones = """
        CREATE TABLE IF NOT EXISTS curso_inscripciones (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            curso_id UUID REFERENCES cursos(id) ON DELETE CASCADE,
            estudiante_id UUID REFERENCES estudiantes(id) ON DELETE CASCADE,
            fecha_inscripcion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            estado TEXT DEFAULT 'activa',
            estado_inscripcion TEXT DEFAULT 'activa',
            monto_pagado DECIMAL(10,2),
            metodo_pago TEXT,
            notas TEXT,
            UNIQUE(curso_id, estudiante_id)
        );
        """
        
        # Ejecutar SQLs
        print("📋 Creando tabla 'cursos'...")
        supabase.rpc('exec_sql', {'sql': sql_cursos}).execute()
        
        print("👥 Creando tabla 'estudiantes'...")
        supabase.rpc('exec_sql', {'sql': sql_estudiantes}).execute()
        
        print("📝 Creando tabla 'curso_inscripciones'...")
        supabase.rpc('exec_sql', {'sql': sql_inscripciones}).execute()
        
        # Verificar que las tablas fueron creadas
        print("\n🔍 Verificando tablas creadas...")
        
        # Verificar tabla cursos
        cursos_test = supabase.table('cursos').select('*').limit(1).execute()
        print("✅ Tabla 'cursos' - OK")
        
        # Verificar tabla estudiantes
        estudiantes_test = supabase.table('estudiantes').select('*').limit(1).execute()
        print("✅ Tabla 'estudiantes' - OK")
        
        # Verificar tabla inscripciones
        inscripciones_test = supabase.table('curso_inscripciones').select('*').limit(1).execute()
        print("✅ Tabla 'curso_inscripciones' - OK")
        
        print("\n🎉 ¡Todas las tablas del módulo CURSOS han sido creadas exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear las tablas: {e}")
        return False

if __name__ == "__main__":
    crear_tablas_cursos()
