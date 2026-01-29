import os
from pathlib import Path


def create_structure():
    base_dir = Path(__file__).parent
    
    examples_dir = base_dir / "examples"
    examples_dir.mkdir(exist_ok=True)
    
    (examples_dir / "basic_usage.py").write_text('''import asyncio
from quick.orm import Quick, models, columns, validators

@models.table("users")
class User(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    username = columns.String(max_length=50, unique=True)
    email = columns.String(max_length=100, unique=True, validators=[validators.Email()])
    age = columns.Integer(nullable=True)

async def main():
    database = Quick(
        host="localhost",
        port=5432,
        database="example_db",
        user="postgres",
        password="password"
    )
    
    await database.connect()
    
    user = await database.insert(User).values(
        username="john_doe",
        email="john@example.com",
        age=25
    ).returning().execute()
    
    print(f"Created user: {user}")
    
    users = await database.select(User).where("age > $1", 18).get()
    print(f"Found {len(users)} users")
    
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
''')
    
    (examples_dir / "relations_example.py").write_text('''import asyncio
from quick.orm import Quick, models, columns, relations

@models.table("users")
class User(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    username = columns.String(max_length=50)
    
    posts = relations.HasMany("posts", foreign_key="user_id")

@models.table("posts")
class Post(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    title = columns.String(max_length=200)
    user_id = columns.Integer()
    
    user = relations.BelongsTo("users", foreign_key="user_id")

async def main():
    database = Quick.from_url("postgresql://postgres:password@localhost/example_db")
    await database.connect()
    
    users = await database.select(User).with_relations("posts").get()
    
    for user in users:
        print(f"User: {user['username']}")
        if hasattr(user, "_posts_loaded"):
            for post in user._posts_loaded:
                print(f"  - Post: {post['title']}")
    
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
''')
    
    (examples_dir / "caching_example.py").write_text('''import asyncio
from quick.orm import Quick, models, columns, CacheManager

@models.table("users")
class User(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    username = columns.String(max_length=50)

async def main():
    database = Quick.from_url("postgresql://postgres:password@localhost/example_db")
    await database.connect()
    
    cache = CacheManager().get_cache("users")
    cache.enable()
    
    query = "SELECT * FROM users WHERE age > $1"
    params = (18,)
    cache_key = cache.generate_key(query, params)
    
    cached = cache.get(cache_key)
    
    if cached:
        print("Using cached result")
        users = cached
    else:
        print("Fetching from database")
        users = await database.select(User).where("age > $1", 18).get()
        cache.set(cache_key, users)
    
    print(f"Found {len(users)} users")
    
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
''')
    
    (examples_dir / "seeding_example.py").write_text('''import asyncio
from quick.orm import Quick, models, columns, Factory, Seeder

@models.table("users")
class User(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    username = columns.String(max_length=50)
    email = columns.String(max_length=100)
    age = columns.Integer()

async def main():
    database = Quick.from_url("postgresql://postgres:password@localhost/example_db")
    await database.connect()
    
    factory = Factory(User).define(
        username=lambda seq, idx: f"user{seq}",
        email=lambda seq, idx: f"user{seq}@example.com",
        age=lambda seq, idx: 20 + idx
    )
    
    users = await factory.seed(database, count=10)
    print(f"Created {len(users)} users")
    
    seeder = Seeder(database)
    await seeder.truncate(User)
    print("Truncated users table")
    
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
''')
    
    print("✓ Created examples directory with sample files")

if __name__ == "__main__":
    create_structure()
