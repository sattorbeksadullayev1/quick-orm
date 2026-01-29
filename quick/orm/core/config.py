from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = ""
    user: str = ""
    password: str = ""
    min_pool_size: int = 10
    max_pool_size: int = 20
    command_timeout: float = 60.0
    query_timeout: float = 60.0
    pool_recycle: int = 3600
    echo: bool = False
    ssl: bool = False
    
    @classmethod
    def from_url(cls, url: str) -> "DatabaseConfig":
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(url)
        
        config = cls(
            host=parsed.hostname or "localhost",
            port=parsed.port or 5432,
            database=parsed.path.lstrip("/") if parsed.path else "",
            user=parsed.username or "",
            password=parsed.password or "",
        )
        
        if parsed.query:
            query_params = parse_qs(parsed.query)
            if "min_pool_size" in query_params:
                config.min_pool_size = int(query_params["min_pool_size"][0])
            if "max_pool_size" in query_params:
                config.max_pool_size = int(query_params["max_pool_size"][0])
            if "ssl" in query_params:
                config.ssl = query_params["ssl"][0].lower() in ("true", "1", "yes")
        
        return config
    
    def to_dsn(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


__all__ = ["DatabaseConfig"]
