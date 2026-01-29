import asyncio
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
