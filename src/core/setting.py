import os
from pathlib import Path
from dotenv import load_dotenv

# ---------- .env discovery ----------
def find_env_file(max_levels: int = 3, filename: str = ".env") -> Path | None:
    """Search for .env file up to `max_levels` parent directories."""
    current = Path.cwd().resolve()
    for _ in range(max_levels + 1):  # include current dir
        candidate = current / filename
        if candidate.exists():
            return candidate
        current = current.parent
    return None

env_path = find_env_file(3)
if env_path:
    load_dotenv(env_path)
    print(f"Loaded .env from {env_path}")
else:
    print("No .env found in 3 levels, using system environment variables only")


# ---------- helpers ----------
def _parse_int_list(csv: str):
    if not csv:
        return []
    return [int(x.strip()) for x in csv.split(",") if x.strip()]

def _get_env_var(name: str, required: bool = True, default=None):
    value = os.getenv(name, default)
    if required and (value is None or value == ""):
        raise RuntimeError(
            f"Missing required environment variable: '{name}'. "
            f"Set it in your system environment or in a .env file."
        )
    return value

def _get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


# ---------- required app vars ----------
BOT_TOKEN = _get_env_var("BOT_TOKEN")
SALATIN = _parse_int_list(_get_env_var("SALATIN", default=""))
PAYCHECK_GROUP_ID = int(_get_env_var("PAYCHECK_GROUP_ID", default="-1"))
GEMMA_API_KEY = _get_env_var("GEMMA_API_KEY")


# ---------- DB config ----------
# Option A: provide DATABASE_URL directly (takes priority if set)
DATABASE_URL = os.getenv("DATABASE_URL")

# Option B: build from primitives if DATABASE_URL is not set
POSTGRES_USER = _get_env_var("POSTGRES_USER", required=DATABASE_URL is None, default=None)
POSTGRES_PASSWORD = _get_env_var("POSTGRES_PASSWORD", required=DATABASE_URL is None, default=None)
POSTGRES_DB = _get_env_var("POSTGRES_DB", required=DATABASE_URL is None, default=None)

# These have sensible defaults for Docker Compose
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_SSLMODE = os.getenv("POSTGRES_SSLMODE")  # e.g. "require" in prod, None in local

# Choose driver family:
#   SYNC:   postgresql+psycopg://   (psycopg3)
#   ASYNC:  postgresql+asyncpg://   (asyncpg)
DB_ASYNC = _get_bool("DB_ASYNC", default=False)

def _build_db_url(
    user: str,
    password: str,
    host: str,
    port: str | int,
    db: str,
    async_mode: bool = False,
    sslmode: str | None = None,
) -> str:
    driver = "postgresql+asyncpg" if async_mode else "postgresql+psycopg"
    # add ?sslmode=... only if provided
    qs = f"?sslmode={sslmode}" if sslmode else ""
    return f"{driver}://{user}:{password}@{host}:{port}/{db}{qs}"

if not DATABASE_URL:
    # Will raise earlier if any of these are missing
    DATABASE_URL = _build_db_url(
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        db=POSTGRES_DB,
        async_mode=DB_ASYNC,
        sslmode=POSTGRES_SSLMODE,
    )

# Convenience
DATABASE_URL_SYNC = (
    DATABASE_URL if not DATABASE_URL.startswith("postgresql+asyncpg")
    else _build_db_url(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, async_mode=False, sslmode=POSTGRES_SSLMODE)
)
DATABASE_URL_ASYNC = (
    DATABASE_URL if DATABASE_URL.startswith("postgresql+asyncpg")
    else _build_db_url(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, async_mode=True, sslmode=POSTGRES_SSLMODE)
)