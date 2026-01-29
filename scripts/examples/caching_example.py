import asyncio
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
