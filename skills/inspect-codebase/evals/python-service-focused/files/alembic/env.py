from alembic import context
from ledgerline.db.models import Base

target_metadata = Base.metadata


def run_migrations_online():
    context.configure(target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


run_migrations_online()
