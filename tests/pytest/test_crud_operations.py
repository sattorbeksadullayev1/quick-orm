import pytest
import pytest_asyncio
from quick.orm import Quick
from quick.orm import models, columns, validators
from quick.orm.exceptions import ValidationError, QueryError


@pytest.fixture
def database_url():
    return "postgresql://postgres:postgres@localhost:5432/test_quick_orm"


@pytest_asyncio.fixture
async def database(database_url):
    db = Quick.from_url(database_url)
    await db.connect()
    yield db
    await db.disconnect()


@models.table("test_users")
class TestUser(models.Model):
    id = columns.Integer(primary_key=True, auto_increment=True)
    username = columns.String(max_length=50, unique=True, validators=[validators.MinLength(3)])
    email = columns.String(max_length=100, unique=True, validators=[validators.Email()])
    age = columns.Integer(nullable=True, validators=[validators.Range(min_value=0, max_value=150)])


@pytest_asyncio.fixture
async def setup_database(database):
    await database.connection_pool.execute("""
        CREATE TABLE IF NOT EXISTS test_users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            age INTEGER
        )
    """)
    
    yield
    
    await database.connection_pool.execute("DROP TABLE IF EXISTS test_users CASCADE")


@pytest.mark.asyncio
async def test_insert_user(database, setup_database):
    result = await database.insert(TestUser).values(
        username="testuser",
        email="test@example.com",
        age=25
    ).returning().execute()
    
    assert result is not None
    assert result["username"] == "testuser"
    assert result["email"] == "test@example.com"
    assert result["age"] == 25


@pytest.mark.asyncio
async def test_select_user(database, setup_database):
    await database.insert(TestUser).values(
        username="selectuser",
        email="select@example.com",
        age=30
    ).execute()
    
    users = await database.select(TestUser).where("username = $1", "selectuser").get()
    
    assert len(users) == 1
    assert users[0]["username"] == "selectuser"
    assert users[0]["age"] == 30


@pytest.mark.asyncio
async def test_update_user(database, setup_database):
    await database.insert(TestUser).values(
        username="updateuser",
        email="update@example.com",
        age=20
    ).execute()
    
    await database.update(TestUser).set(age=21).where("username = $1", "updateuser").execute()
    
    users = await database.select(TestUser).where("username = $1", "updateuser").get()
    
    assert users[0]["age"] == 21


@pytest.mark.asyncio
async def test_delete_user(database, setup_database):
    await database.insert(TestUser).values(
        username="deleteuser",
        email="delete@example.com",
        age=40
    ).execute()
    
    await database.delete(TestUser).where("username = $1", "deleteuser").execute()
    
    users = await database.select(TestUser).where("username = $1", "deleteuser").get()
    
    assert len(users) == 0


@pytest.mark.asyncio
async def test_bulk_insert(database, setup_database):
    users = await database.bulk_insert(TestUser).values(
        {"username": "bulk1", "email": "bulk1@example.com", "age": 25},
        {"username": "bulk2", "email": "bulk2@example.com", "age": 30},
        {"username": "bulk3", "email": "bulk3@example.com", "age": 35}
    ).returning().execute()
    
    assert len(users) == 3
    assert users[0]["username"] == "bulk1"
    assert users[1]["username"] == "bulk2"
    assert users[2]["username"] == "bulk3"


@pytest.mark.asyncio
async def test_count(database, setup_database):
    await database.bulk_insert(TestUser).values(
        {"username": "count1", "email": "count1@example.com"},
        {"username": "count2", "email": "count2@example.com"},
        {"username": "count3", "email": "count3@example.com"}
    ).execute()
    
    count = await database.select(TestUser).count()
    
    assert count >= 3


@pytest.mark.asyncio
async def test_pagination(database, setup_database):
    await database.bulk_insert(TestUser).values(
        {"username": f"page{i}", "email": f"page{i}@example.com", "age": i}
        for i in range(1, 11)
    ).execute()
    
    result = await database.select(TestUser).order_by("id ASC").paginate(page=1, per_page=5)
    
    assert result["current_page"] == 1
    assert result["per_page"] == 5
    assert len(result["data"]) == 5
    assert result["total"] >= 10


@pytest.mark.asyncio
async def test_transaction_commit(database, setup_database):
    async with database.transaction():
        await database.insert(TestUser).values(
            username="transaction_user",
            email="transaction@example.com",
            age=50
        ).execute()
    
    users = await database.select(TestUser).where("username = $1", "transaction_user").get()
    
    assert len(users) == 1


@pytest.mark.asyncio
async def test_transaction_rollback(database, setup_database):
    try:
        async with database.transaction():
            await database.insert(TestUser).values(
                username="rollback_user",
                email="rollback@example.com",
                age=50
            ).execute()
            raise Exception("Force rollback")
    except Exception:
        pass
    
    users = await database.select(TestUser).where("username = $1", "rollback_user").get()
    
    assert len(users) == 0
