from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import logging


class SQLAlchemy:
    def __init__(self, app: FastAPI = None, **kwargs) -> None:
        self._engine = None
        self._session = None
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs) -> None:
        """DB initialization function"""

        database_url = kwargs.get("DB_URL")
        pool_recycle = kwargs.setdefault("DB_POOL_RECYCLE", 900)  # what is this
        echo = kwargs.setdefault("DB_ECHO", True)  # what is this

        self._engine = create_engine(
            database_url,
            echo=echo,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )
        self._session = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

        @app.on_event("startup")
        def on_app_start():
            self._engine.connect()
            logging.info("DB connected.")

        @app.on_event("shutdown")
        def on_app_shutdown():
            self._session.close_all()
            self._engine.dispose()
            logging.info("DB disconnected")

    def get_db(self) -> Session:
        """function to maintain DB session"""
        if self._session is None:
            raise Exception("must call 'init_app' first.")
        db_session = None
        try:
            db_session = self._session()
            yield db_session
        finally:
            db_session.close()

    @property
    def session(self):
        return self.get_db

    @property
    def engine(self):
        return self._engine

    def create_tables(self):
        Base.metadata.create_all(bind=self._engine, checkfirst=True)


database = SQLAlchemy()
Base = (
    declarative_base()
)  # instance of base class which maintains a catalog of classes & tables relative to that base
