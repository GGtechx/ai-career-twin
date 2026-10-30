"""
Generates standard PostgreSQL DDL from SQLAlchemy models and saves to schema.sql
"""
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from app.core.database import Base
import app.models

schema_sql_path = os.path.join(os.path.dirname(__file__), "schema.sql")

with open(schema_sql_path, "w", encoding="utf-8") as f:
    f.write("-- ============================================================================\n")
    f.write("-- AI DIGITAL CAREER TWIN - POSTGRESQL DATABASE SCHEMA (21 TABLES)\n")
    f.write("-- Generated for PostgreSQL 14+ / 15+ / 16+\n")
    f.write("-- ============================================================================\n\n")

    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))
        f.write(f"-- Table: {table.name}\n")
        f.write(ddl.strip() + ";\n\n")

print(f"Generated PostgreSQL DDL for {len(Base.metadata.sorted_tables)} tables into {schema_sql_path}")
