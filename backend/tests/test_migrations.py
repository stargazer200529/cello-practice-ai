from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from app.database import PieceEntity


def test_migration_chain_upgrades_and_downgrades(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'migration.db'}"
    engine = create_engine(database_url)
    PieceEntity.__table__.create(engine)
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    config.set_main_option("script_location", str(Path(__file__).parents[1] / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(config, "head")
    assert {"practice_sessions", "practice_segments", "recordings"}.issubset(inspect(engine).get_table_names())

    command.downgrade(config, "base")
    assert "practice_sessions" not in inspect(engine).get_table_names()
    assert "practice_segments" not in inspect(engine).get_table_names()
    assert "recordings" not in inspect(engine).get_table_names()
