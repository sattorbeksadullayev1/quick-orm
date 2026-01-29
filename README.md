# Quick-OPG

Async PostgreSQL ORM with YAML-based model generation.

## Overview

Quick-OPG is a modern async ORM for PostgreSQL that uses YAML configuration to generate Python models. It provides a fluent query builder, relationship management, and built-in validation.

## Installation

```bash
pip install quick-opg
```

## Quick Start

Initialize a new project:

```bash
quick init
```

This creates `quick.yaml` configuration file. Define your models:

```yaml
database:
  host: localhost
  port: 5432
  database: mydb
  user: postgres
  password: secret

models:
  directory: models
  definitions:
    - name: users
      model: User
      columns:
        - name: id
          type: uuid
          primary_key: true
          auto_generate: true
        - name: username
          type: string
          max_length: 50
          unique: true
          validators:
            - type: min_length
              value: 3
        - name: email
          type: string
          max_length: 100
          validators:
            - type: email
        - name: age
          type: integer
          nullable: true
        - name: created_at
          type: datetime
          auto_now_add: true
      relations:
        - name: posts
          type: has_many
          target: posts
          foreign_key: user_id

    - name: posts
      model: Post
      columns:
        - name: id
          type: integer
          primary_key: true
          auto_increment: true
        - name: user_id
          type: uuid
        - name: title
          type: string
          max_length: 200
        - name: content
          type: text
        - name: published_at
          type: datetime
          nullable: true
      relations:
        - name: user
          type: belongs_to
          target: users
          foreign_key: user_id
```

Generate Python models from YAML:

```bash
quick generate
```

Use in your application:

```python
from quick.orm import Quick
from models import User, Post

async def main():
    db = Quick("postgresql://user:pass@localhost/mydb")
    await db.connect()
    
    # Create user
    user = await db.insert(User).values(
        username="john_doe",
        email="john@example.com",
        age=25
    ).returning().execute()
    
    # Query with conditions
    users = await db.select(User).where("age > $1", 18).order_by("username").get()
    
    # Update
    await db.update(User).set(age=26).where("id = $1", user.id).execute()
    
    # Delete
    await db.delete(User).where("id = $1", user.id).execute()
    
    await db.disconnect()
```

## Features

**YAML Model Generation**  
Define models in YAML and generate Python code automatically.

**Async First**  
Built on asyncpg for high-performance async operations.

**Relations**  
Support for HasMany, BelongsTo, HasOne, ManyToMany, and Polymorphic relations.

**Query Builder**  
Fluent interface for building complex queries.

**Migrations**  
Schema management with up/down migrations.

**Validation**  
Built-in validators for common data types.

**CLI Tools**  
Command-line interface for common tasks.

## CLI Commands

```bash
quick init                     # Initialize project
quick generate                 # Generate models from YAML
quick migrate run              # Run migrations
quick migrate rollback         # Rollback last migration
quick migrate status           # Show migration status
quick db tables                # List all tables
quick db columns <table>       # Show table columns
```

## Column Types

- Integer types: `integer`, `bigint`, `smallint`
- Numeric types: `float`, `decimal`
- Text types: `string`, `text`, `char`
- Other types: `uuid`, `boolean`, `datetime`, `date`, `time`, `json`, `jsonb`, `binary`, `array`

## Validators

- String: `min_length`, `max_length`, `regex`, `email`, `url`, `phone_number`
- Numeric: `range`, `positive`, `negative`, `non_negative`, `non_positive`

## Relations

- `belongs_to` - Many-to-one
- `has_one` - One-to-one
- `has_many` - One-to-many
- `many_to_many` - Many-to-many
- `morph_to`, `morph_one`, `morph_many` - Polymorphic relations
- `has_many_through` - Through intermediate model

## Requirements

- Python 3.10+
- PostgreSQL 13+
- asyncpg 0.29+

## License

MIT License - Copyright (c) 2026 Sattorbek Sa'dullayev
