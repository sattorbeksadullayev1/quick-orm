# Quick-OPG

Async PostgreSQL ORM with YAML-based model generation and fluent query builder.

## Features

- 🚀 Async-first with asyncpg
- 📝 YAML-based model generation
- 🔗 Relations support (HasMany, BelongsTo, ManyToMany, Polymorphic)
- 💾 Query caching with TTL
- 🌱 Database seeding
- 🗑️ Soft deletes
- 🛠️ CLI tool
- ✅ Built-in validators

## Installation

```bash
pip install quick-opg
```

## Quick Start

### 1. Initialize

```bash
quick init
```

### 2. Define models in `quick.yaml`

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
        - name: username
          type: string
          max_length: 50
          unique: true
        - name: email
          type: string
          validators:
            - type: email
```

### 3. Generate models

```bash
quick generate
```

### 4. Use in your code

```python
from quick.orm import Quick

db = Quick("postgresql://user:pass@localhost/mydb")
await db.connect()

# Insert
user = await db.insert(User).values(
    username="john",
    email="john@example.com"
).returning().execute()

# Query
users = await db.select(User).where("age > $1", 18).get()

# Update
await db.update(User).set(age=26).where("id = $1", user_id).execute()

# Delete
await db.delete(User).where("id = $1", user_id).execute()
```

## CLI Commands

```bash
quick init                    # Initialize project
quick generate               # Generate models from YAML
quick migrate run            # Run migrations
quick migrate rollback       # Rollback last migration
quick db tables              # List tables
quick db columns <table>     # Show table columns
```

## Requirements

- Python 3.10+
- PostgreSQL 13+

## License

MIT
