from dataclasses import dataclass, asdict
from os import path, environ

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@dataclass
class Config:
    PROJECT_NAME: str = "handy-data-mesh"
    PROJECT_VERSION: str = "1.0.0"

    BASE_DIR = base_dir
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True


@dataclass
class ProdConfig(Config):
    BOOTSTRAP_SERVERS = {
        "bootstrap.servers": "jun-kafka-0.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,"
                             "jun-kafka-1.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,"
                             "jun-kafka-2.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092"
    }
    KSQL_SERVER = "http://0.0.0.0:8090"


@dataclass
class LocalConfig(Config):
    PROJ_RELOAD: bool = True

    # postgres setting
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_DB: str = "testdb"
    DB_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    BOOTSTRAP_SERVERS = {
        "bootstrap.servers": "jun-kafka-0.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,"
                             "jun-kafka-1.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092,"
                             "jun-kafka-2.jun-kafka-headless.jun-test-kafka.svc.cluster.local:9092"
    }
    KSQL_SERVER = "http://0.0.0.0:8090"


def conf() -> dict:
    config = dict(prod=ProdConfig(), local=LocalConfig())
    config_dict = asdict(config.get(environ.get("API_ENV", "local")))

    return config_dict
