# Quick-ORM

Async PostgreSQL ORM with strong type hints and Laravel-style API.

## Features

- 🚀 **Async-first** - Built on asyncpg for high performance
- 🔒 **Type-safe** - Full type hints with generics support
- 🎯 **Simple API** - Laravel/Eloquent-inspired fluent interface
- 🔗 **Relations** - BelongsTo, HasOne, HasMany, ManyToMany, Polymorphic, Through
- 📊 **Query Builder** - Powerful query construction with method chaining
- 🔄 **Migrations** - Schema management with up/down migrations
- 🛠️ **CLI Tool** - Command-line interface for migrations and database management
- ✅ **Validators** - Built-in field validation
- 💾 **Caching** - Query result caching with TTL
- 🔍 **Query Logger** - SQL query logging and profiling
- 🌱 **Seeding** - Database seeding with factories
- 🎯 **Scopes** - Global and local query scopes
- 🗑️ **Soft Deletes** - Soft delete support with restore
- ⚡ **Connection Retry** - Automatic connection retry with exponential backoff
- 🎨 **Rich Errors** - Beautiful error formatting with Rich

## Installation

```bash
pip install quick-orm
```

## Quick Start

### Initialize Project

```bash
quick init
```

This creates:
- `quick.yaml` - Database configuration file
- `migrations/` - Directory for migration files
- `models/` - Directory for model definitions

Edit `quick.yaml` with your database credentials and model definitions:

```yaml
database:
  host: localhost
  port: 5432
  user: postgres
  password: postgres
  database: test_db
migrations:
  directory: migrations
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
          unique: true
          validators:
            - type: email
        - name: created_at
          type: datetime
          auto_now_add: true
      relations:
        - name: posts
          type: has_many
          target: posts
          foreign_key: user_id
```

### Generate Models

```bash
quick generate
```

This generates Python model files from your YAML configuration. Example output:

```python
from quick.orm import models, columns, validators, relations


@models.table("users")
class User(models.Model):
    id = columns.UUID(primary_key=True, auto_generate=True)
    username = columns.String(unique=True, max_length=50, validators=[validators.MinLength(3)])
    email = columns.String(unique=True, max_length=100, validators=[validators.Email()])
    created_at = columns.DateTime(auto_now_add=True)
    
    posts = relations.HasMany("posts", foreign_key="user_id")
```

### Database Operations

```python
import asyncio
from quick.orm import Quick

async def main():
    database = Quick(
        host="localhost",
        port=5432,
        database="mydb",
        user="postgres",
        password="password"
    )
    
    await database.connect()
    
    user = await database.insert(User).values(
        username="john_doe",
        email="john@example.com",
        age=25
    ).returning().execute()
    
    users = await database.select(User).where("age > $1", 18).get()
    
    await database.update(User).set(age=26).where("username = $1", "john_doe").execute()
    
    await database.delete(User).where("age < $1", 18).execute()
    
    await database.disconnect()

asyncio.run(main())
```

### Query Builder

```python
users = await database.select(User).where("age > $1", 18).order_by("username ASC").limit(10).get()

user = await database.select(User).where("email = $1", "john@example.com").first()

count = await database.select(User).where("age > $1", 18).count()

paginated = await database.select(User).paginate(page=1, per_page=15)
```

### Eager Loading

```python
users = await database.select(User).with_relations("posts", "profile").get()

for user in users:
    print(user.username, user.posts)
```

### Aggregations

```python
total_age = await database.select(User).sum("age")
avg_age = await database.select(User).avg("age")
min_age = await database.select(User).min("age")
max_age = await database.select(User).max("age")
```

### Joins and GROUP BY

```python
results = await (
    database.select(User)
    .select("users.username", "COUNT(posts.id) as post_count")
    .join("posts", "users.id = posts.user_id")
    .group_by("users.username")
    .having("COUNT(posts.id) > $1", 5)
    .get()
)
```

### Transactions

```python
async with database.transaction() as tx:
    await tx.execute("INSERT INTO users (username) VALUES ($1)", "new_user")
    await tx.execute("UPDATE posts SET title = $1 WHERE user_id = $2", "New Title", user_id)
```

### Bulk Operations

```python
users = await database.bulk_insert(User).values(
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"},
    {"username": "user3", "email": "user3@example.com"},
).returning().execute()

updated_count = await database.bulk_update(User).add_update(
    {"age": 26}, "username = $1", "user1"
).add_update(
    {"age": 31}, "username = $1", "user2"
).execute()
```

## CLI Tool

### Initialize Project

Create a new Quick-ORM project:
```bash
quick init
```

This generates:
- `quick.yaml` - Configuration file
- `migrations/` - Migration directory
- `models/` - Models directory

### Migrations

Create a new migration:
```bash
quick migrate make create_users_table
```

Run pending migrations:
```bash
quick migrate run --database postgresql://user:pass@localhost/db
```

Rollback last migration:
```bash
quick migrate rollback
```

Reset all migrations:
```bash
quick migrate reset
```

Check migration status:
```bash
quick migrate status
```

### Database Inspection

List all tables:
```bash
quick db tables
```

Show table columns:
```bash
quick db columns users
```

### Generate Models

Generate models from YAML configuration:
```bash
quick generate --config quick.yaml
```

## YAML Configuration

### Model Definition

```yaml
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
          unique: true
          validators:
            - type: email
        - name: age
          type: integer
          nullable: true
          validators:
            - type: range
              min_value: 0
              max_value: 150
        - name: created_at
          type: datetime
          auto_now_add: true
        - name: updated_at
          type: datetime
          auto_now: true
      relations:
        - name: posts
          type: has_many
          target: posts
          foreign_key: user_id
        - name: profile
          type: has_one
          target: profiles
          foreign_key: user_id
```

### Supported Column Types

- `integer`, `bigint`, `smallint` - Integer types
- `float`, `decimal` - Floating point types
- `string`, `text`, `char` - Text types
- `uuid` - UUID type
- `boolean` - Boolean type
- `datetime`, `date`, `time` - Temporal types
- `json`, `jsonb` - JSON types
- `binary` - Binary data
- `array` - Array type

### Supported Validators

- `min_length`, `max_length` - String length
- `regex` - Regular expression
- `email`, `url`, `phone_number` - Format validators
- `range` - Numeric range
- `positive`, `negative` - Sign validators
- `non_negative`, `non_positive` - Sign validators with zero

### Supported Relations

- `belongs_to` - Many-to-one relationship
- `has_one` - One-to-one relationship
- `has_many` - One-to-many relationship
- `many_to_many` - Many-to-many relationship
- `morph_to` - Polymorphic many-to-one
- `morph_one` - Polymorphic one-to-one
- `morph_many` - Polymorphic one-to-many
- `has_many_through` - Has many through intermediate model

## Advanced Features

### Query Caching

```python
from quick.orm import CacheManager

cache = CacheManager().get_cache("default")
cache.enable()

cache_key = cache.generate_key("SELECT * FROM users WHERE age > $1", (18,))
cached_result = cache.get(cache_key)

if not cached_result:
    result = await database.select(User).where("age > $1", 18).get()
    cache.set(cache_key, result)
```

### Query Logging

```python
from quick.orm import QueryLogger

logger = QueryLogger(log_file="queries.log", log_slow_queries=1000)
logger.log_query("SELECT * FROM users", params=(1,), duration_ms=250)

stats = logger.get_stats()
slow_queries = logger.get_queries(slow_only=True)
```

### Database Seeding

```python
from quick.orm import Seeder, Factory

factory = Factory(User).define(
    username=lambda seq, idx: f"user{seq}",
    email=lambda seq, idx: f"user{seq}@example.com",
    age=lambda seq, idx: 20 + idx
)

users_data = factory.create(count=10)
await factory.seed(database, count=10)

seeder = Seeder(database)
await seeder.seed(User, [
    {"username": "admin", "email": "admin@example.com"},
    {"username": "user1", "email": "user1@example.com"}
])

await seeder.seed_from_json(User, "seeds/users.json")
await seeder.truncate(User)
```

### Soft Deletes

```python
from quick.orm import SoftDeleteMixin
from quick.orm import models, columns

@models.table("posts")
class Post(models.Model, SoftDeleteMixin):
    id = columns.Integer(primary_key=True, auto_increment=True)
    title = columns.String(max_length=200)
    deleted_at = columns.DateTime(nullable=True)

post = await database.select(Post).where("id = $1", 1).first()

await post.soft_delete(database)
await post.restore(database)
await post.force_delete(database)
```

### Query Scopes

```python
from quick.orm import SoftDeleteScope, PublishedScope, ActiveScope

class User(models.Model):
    pass

User.add_global_scope(SoftDeleteScope())
User.add_global_scope(ActiveScope())

users = await database.select(User).get()
all_users = await User.without_global_scopes(database.select(User)).get()
```

### Polymorphic Relations

```python
from quick.orm.relations import MorphTo, MorphMany

@models.table("images")
class Image(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    url = columns.String(max_length=255)
    imageable_type = columns.String(max_length=50)
    imageable_id = columns.Integer()
    
    imageable = MorphTo()

@models.table("posts")
class Post(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    title = columns.String(max_length=200)
    
    images = MorphMany("images", morph_name="imageable")

@models.table("users")
class User(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    username = columns.String(max_length=50)
    
    images = MorphMany("images", morph_name="imageable")
```

### Has Many Through

```python
from quick.orm.relations import HasManyThrough

@models.table("countries")
class Country(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    name = columns.String(max_length=100)
    
    posts = HasManyThrough(
        related_model="posts",
        through_model="users",
        first_key="country_id",
        second_key="user_id"
    )

@models.table("users")
class User(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    country_id = columns.Integer()

@models.table("posts")
class Post(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    user_id = columns.Integer()
```

## Testing

Run tests with pytest:

```bash
pytest tests/pytest/ -v
```

Run specific test file:

```bash
pytest tests/pytest/test_cache.py -v
pytest tests/pytest/test_exceptions.py -v
pytest tests/pytest/test_generator.py -v
```

## Migration Example

```python
from quick.orm.migrations import Migration, SchemaBuilder

class CreateUsersTable(Migration):
    name = "2024_01_01_create_users_table"
    
    async def up(self, database) -> None:
        schema = SchemaBuilder(database)
        
        def create_users(table):
            table.big_id()
            table.string("username", 50).unique = True
            table.string("email", 100).unique = True
            table.string("password", 255)
            table.integer("age").nullable = True
            table.timestamps()
        
        await schema.create_table("users", create_users)
    
    async def down(self, database) -> None:
        schema = SchemaBuilder(database)
        await schema.drop_table("users")
```

## Column Types

- `Integer()`, `BigInt()`, `SmallInt()`
- `String(max_length)`, `Text()`, `Char(length)`
- `Float()`, `Decimal(precision, scale)`
- `Boolean()`
- `Date()`, `Time()`, `DateTime()`
- `UUID()`
- `JSON()`, `JSONB()`
- `Binary()`
- `Array(item_type)`

## Validators

- `MinLength(min)`, `MaxLength(max)`
- `Regex(pattern)`
- `Email()`, `URL()`, `PhoneNumber()`
- `Range(min_value, max_value)`
- `Positive()`, `Negative()`
- `NonNegative()`, `NonPositive()`

## Requirements

- Python 3.11+
- PostgreSQL 13+
- asyncpg 0.29+

## License

MIT
