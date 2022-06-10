from pydantic import BaseModel


class Item(BaseModel):
    name: str


class EtlConfig(BaseModel):
    source_type: str
    source_db_name: str
    source_db_host: str
    source_db_port: str
    source_table_name: str
    target_type: str
    target_db_name: str
    target_db_host: str
    target_db_port: str
    target_table_name: str



