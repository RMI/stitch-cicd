from __future__ import annotations

from typing import Callable, Protocol

from sqlalchemy.orm import Session

from stitch.core.resources.domain.ports.repositories import (
    MembershipRepository,
    ResourceRepository,
)
from stitch.core.resources.domain.ports.sources import (
    SourcePersistenceRepository,
    SourceRegistry,
    SourceRegistryFactory,
)


class TransactionContext(Protocol):
    resources: ResourceRepository
    memberships: MembershipRepository
    source_registry: SourceRegistry

    def __enter__(self) -> TransactionContext:
        """Begin transaction"""

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Commit or rollback based on exception status"""

    def commit(self) -> None:
        """Explicitly commit transaction"""

    def rollback(self) -> None:
        """Explicitly rollback transaction"""
