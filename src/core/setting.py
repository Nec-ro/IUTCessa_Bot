import os
from pathlib import Path
from dotenv import load_dotenv

def find_env_file(max_levels: int = 3, filename: str = ".env") -> Path | None:
    """Search for .env file up to `max_levels` parent directories."""
    current = Path.cwd().resolve()
    for _ in range(max_levels + 1):  # include current dir
        candidate = current / filename
        if candidate.exists():
            return candidate
        current = current.parent
    return None

# Look for .env up to 3 levels above CWD
env_path = find_env_file(3)

if env_path:
    load_dotenv(env_path)
    print(f"Loaded .env from {env_path}")
else:
    print("No .env found in 3 levels, using system environment variables only")


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

# Required variables
BOT_TOKEN = _get_env_var("BOT_TOKEN")
SALATIN = _parse_int_list(_get_env_var("SALATIN", default=""))
PAYCHECK_GROUP_ID = int(_get_env_var("PAYCHECK_GROUP_ID", default="-1"))
GEMMA_API_KEY = _get_env_var("GEMMA_API_KEY")