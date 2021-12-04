from app.common.config import conf
from app.utils.io_utils import database
from fastapi import FastAPI


def create_app() -> FastAPI:
    config_dict = conf()
    app = FastAPI()

    # DB initialization
    # database.init_app(app, **config_dict)
    # database.create_tables()

    return app


amazon_rest_api_client = create_app()
