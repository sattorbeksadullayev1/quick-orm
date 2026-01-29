import asyncio
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
