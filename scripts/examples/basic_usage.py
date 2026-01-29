import asyncio
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
