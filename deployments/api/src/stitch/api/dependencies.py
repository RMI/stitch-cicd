from typing import Annotated
from fastapi import Depends
from stitch.core.resources.app.services.resource_service import ResourceService
from stitch.core.resources.adapters.sql.sql_transaction_context import (
    SQLTransactionContext,
)
from stitch.core.resources.adapters.sql.settings import PostgresConfig
from stitch.core.resources.adapters.sql.connect import Session

from stitch.api.db import create_field_registry


ConfigDep = Annotated[PostgresConfig, Depends()]


def get_resource_service(config: ConfigDep) -> ResourceService:
    session = Session(config=config)
    tx = SQLTransactionContext(
        session_factory=session, source_factory=create_field_registry
    )
    return ResourceService(tx_ctx=tx)
