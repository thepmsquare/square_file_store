import importlib
import os

import pytest
from fastapi.testclient import TestClient


def patched_join(*args):

    *rest, last = args
    if last == "config.ini":
        last = "config.testing.ini"

    return original_join(*rest, last)


original_join = os.path.join


@pytest.fixture
def get_patched_configuration(monkeypatch, tmp_path):
    import square_file_store.configuration

    monkeypatch.setattr(os.path, "join", patched_join)
    importlib.reload(square_file_store.configuration)
    return square_file_store.configuration


@pytest.fixture
def create_client_and_cleanup(get_patched_configuration):
    from square_database_structure import create_database_and_tables
    from square_file_store.main import (
        app,
    )

    create_database_and_tables(
        db_username=get_patched_configuration.config_str_db_username,
        db_port=get_patched_configuration.config_int_db_port,
        db_password=get_patched_configuration.config_str_db_password,
        db_ip=get_patched_configuration.config_str_db_ip,
    )
    client = TestClient(app)
    yield client
    from sqlalchemy import text, create_engine
    from square_database_structure.main import global_list_create

    local_str_postgres_url = (
        f"postgresql://{get_patched_configuration.config_str_db_username}:{get_patched_configuration.config_str_db_password}@"
        f"{get_patched_configuration.config_str_db_ip}:{str(get_patched_configuration.config_int_db_port)}/"
    )

    postgres_engine = create_engine(local_str_postgres_url)

    with postgres_engine.connect() as postgres_connection:

        postgres_connection.execute(text("commit"))

        for database in global_list_create:

            postgres_connection.execute(
                text(f"DROP DATABASE {database['database']} WITH (FORCE)")
            )
