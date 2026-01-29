import click
from pathlib import Path
from datetime import datetime
import yaml


@click.group()
def cli():
    pass


@cli.command()
def init():
    config_path = Path("quick.yaml")
    migrations_dir = Path("migrations")
    models_dir = Path("models")
    
    if config_path.exists():
        click.echo(click.style("✗ Configuration file already exists!", fg="red"))
        return
    
    default_config = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "postgres",
            "database": "test_db"
        },
        "migrations": {
            "directory": "migrations"
        },
        "models": {
            "directory": "models",
            "definitions": [
                {
                    "name": "users",
                    "model": "User",
                    "columns": [
                        {
                            "name": "id",
                            "type": "uuid",
                            "primary_key": True,
                            "auto_generate": True
                        },
                        {
                            "name": "username",
                            "type": "string",
                            "max_length": 50,
                            "unique": True,
                            "validators": [
                                {"type": "min_length", "value": 3}
                            ]
                        },
                        {
                            "name": "email",
                            "type": "string",
                            "max_length": 100,
                            "unique": True,
                            "validators": [
                                {"type": "email"}
                            ]
                        },
                        {
                            "name": "created_at",
                            "type": "datetime",
                            "auto_now_add": True
                        }
                    ],
                    "relations": []
                }
            ]
        }
    }
    
    with open(config_path, "w") as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
    
    migrations_dir.mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)
    
    click.echo(click.style("✓ Initialized Quick-ORM project:", fg="green"))
    click.echo(f"  - Created {config_path}")
    click.echo(f"  - Created {migrations_dir}/")
    click.echo(f"  - Created {models_dir}/")
    click.echo()
    click.echo(click.style("Next steps:", fg="cyan"))
    click.echo("  1. Edit quick.yaml with your database credentials")
    click.echo("  2. Create models in the models/ directory")
    click.echo("  3. Run: quick migrate make create_initial_tables")
    click.echo("  4. Run: quick migrate run")


@cli.group()
def migrate():
    pass


@migrate.command()
@click.option("--database", default="postgresql://postgres:postgres@localhost:5432/test_db", help="Database URL")
def run(database: str):
    import asyncio
    from quick.orm import Quick
    from quick.orm.migrations import MigrationRunner
    
    async def execute():
        db = Quick.from_url(database)
        await db.connect()
        
        try:
            runner = MigrationRunner(db)
            executed = await runner.run()
            
            if executed:
                click.echo(click.style(f"✓ Executed {len(executed)} migration(s):", fg="green"))
                for migration in executed:
                    click.echo(f"  - {migration}")
            else:
                click.echo(click.style("No pending migrations", fg="yellow"))
        finally:
            await db.disconnect()
    
    asyncio.run(execute())


@migrate.command()
@click.option("--database", default="postgresql://postgres:postgres@localhost:5432/test_db", help="Database URL")
@click.option("--steps", default=1, help="Number of migration batches to rollback")
def rollback(database: str, steps: int):
    import asyncio
    from quick.orm import Quick
    from quick.orm.migrations import MigrationRunner
    
    async def execute():
        db = Quick.from_url(database)
        await db.connect()
        
        try:
            runner = MigrationRunner(db)
            rolled_back = await runner.rollback(steps)
            
            if rolled_back:
                click.echo(click.style(f"✓ Rolled back {len(rolled_back)} migration(s):", fg="green"))
                for migration in rolled_back:
                    click.echo(f"  - {migration}")
            else:
                click.echo(click.style("No migrations to rollback", fg="yellow"))
        finally:
            await db.disconnect()
    
    asyncio.run(execute())


@migrate.command()
@click.option("--database", default="postgresql://postgres:postgres@localhost:5432/test_db", help="Database URL")
def reset(database: str):
    import asyncio
    from quick.orm import Quick
    from quick.orm.migrations import MigrationRunner
    
    async def execute():
        db = Quick.from_url(database)
        await db.connect()
        
        try:
            runner = MigrationRunner(db)
            rolled_back = await runner.reset()
            
            if rolled_back:
                click.echo(click.style(f"✓ Reset {len(rolled_back)} migration(s):", fg="green"))
                for migration in rolled_back:
                    click.echo(f"  - {migration}")
            else:
                click.echo(click.style("No migrations to reset", fg="yellow"))
        finally:
            await db.disconnect()
    
    asyncio.run(execute())


@migrate.command()
@click.option("--database", default="postgresql://postgres:postgres@localhost:5432/test_db", help="Database URL")
def status(database: str):
    import asyncio
    from quick.orm import Quick
    from quick.orm.migrations import MigrationRunner
    
    async def execute():
        db = Quick.from_url(database)
        await db.connect()
        
        try:
            runner = MigrationRunner(db)
            migrations = await runner.status()
            
            if migrations:
                click.echo(click.style("Migration Status:", fg="cyan", bold=True))
                for migration in migrations:
                    status_icon = "✓" if migration["executed"] else "✗"
                    status_color = "green" if migration["executed"] else "red"
                    click.echo(f"  {click.style(status_icon, fg=status_color)} {migration['name']}")
            else:
                click.echo(click.style("No migrations found", fg="yellow"))
        finally:
            await db.disconnect()
    
    asyncio.run(execute())


@migrate.command()
@click.argument("name")
def make(name: str):
    migrations_dir = Path("migrations")
    migrations_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    filename = f"{timestamp}_{name}.py"
    filepath = migrations_dir / filename
    
    template = f'''from quick.orm.migrations import Migration, SchemaBuilder


class {_to_class_name(name)}(Migration):
    name = "{timestamp}_{name}"
    
    async def up(self, database) -> None:
        schema = SchemaBuilder(database)
        
        def create_table(table):
            table.id()
            table.timestamps()
        
        await schema.create_table("table_name", create_table)
    
    async def down(self, database) -> None:
        schema = SchemaBuilder(database)
        await schema.drop_table("table_name")
'''
    
    filepath.write_text(template)
    click.echo(click.style(f"✓ Created migration: {filename}", fg="green"))


def _to_class_name(snake_case: str) -> str:
    return "".join(word.capitalize() for word in snake_case.split("_"))


@cli.command()
@click.option("--config", default="quick.yaml", help="Configuration file path")
def generate(config: str):
    from quick.orm.generator import ModelParser, CodeGenerator
    
    try:
        parser = ModelParser(config)
        models = parser.get_models()
        
        if not models:
            click.echo(click.style("✗ No models defined in configuration", fg="red"))
            return
        
        for model in models:
            parser.validate_model(model)
        
        output_dir = parser.get_model_directory()
        generator = CodeGenerator(output_dir)
        
        generated_files = generator.generate_all(models)
        
        click.echo(click.style(f"✓ Generated {len(models)} model(s):", fg="green"))
        for filepath in generated_files:
            click.echo(f"  - {filepath}")
        
        click.echo()
        click.echo(click.style("Next steps:", fg="cyan"))
        click.echo("  1. Review generated models in the models/ directory")
        click.echo("  2. Run: quick migrate make create_initial_tables")
        click.echo("  3. Edit migration file to match your models")
        click.echo("  4. Run: quick migrate run")
        
    except FileNotFoundError as e:
        click.echo(click.style(f"✗ {e}", fg="red"))
    except ValueError as e:
        click.echo(click.style(f"✗ Validation error: {e}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"✗ Error: {e}", fg="red"))


@cli.group()
def db():
    pass


@db.command()
@click.option("--database", default="postgresql://postgres:postgres@localhost:5432/test_db", help="Database URL")
def tables(database: str):
    import asyncio
    from quick.orm import Quick
    
    async def execute():
        db = Quick.from_url(database)
        await db.connect()
        
        try:
            table_list = await db.schema.get_tables()
            
            if table_list:
                click.echo(click.style("Database Tables:", fg="cyan", bold=True))
                for table in table_list:
                    click.echo(f"  - {table}")
            else:
                click.echo(click.style("No tables found", fg="yellow"))
        finally:
            await db.disconnect()
    
    asyncio.run(execute())


@db.command()
@click.argument("table")
@click.option("--database", default="postgresql://postgres:postgres@localhost:5432/test_db", help="Database URL")
def columns(table: str, database: str):
    import asyncio
    from quick.orm import Quick
    
    async def execute():
        db = Quick.from_url(database)
        await db.connect()
        
        try:
            cols = await db.schema.get_columns(table)
            
            if cols:
                click.echo(click.style(f"Columns in {table}:", fg="cyan", bold=True))
                for col in cols:
                    nullable = "NULL" if col["nullable"] else "NOT NULL"
                    click.echo(f"  - {col['name']}: {col['type']} {nullable}")
            else:
                click.echo(click.style(f"Table '{table}' not found", fg="red"))
        finally:
            await db.disconnect()
    
    asyncio.run(execute())


if __name__ == "__main__":
    cli()
