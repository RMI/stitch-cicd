from typing import Protocol
from collections.abc import Sequence

from stitch.core.resources.domain.entities import (
    ResourceEntity,
)
from stitch.core.resources.domain.entities import MembershipEntity


class ResourceRepository(Protocol):
    def create(
        self,
        dataset: str | None = None,
        source_pk: str | None = None,
        repointed_id: int | None = None,
        name: str | None = None,
        country_iso3: str | None = None,
        operator: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> int:
        """Create new resource mapping and return unique resource identifier"""

    def get(self, resource_id: int) -> ResourceEntity | None:
        """Retrieve resource by identifier"""

    def find_root_resource(self, resource_id: int) -> ResourceEntity:
        """Follow the id repointing until we find an "unrepointed" resource"""

    def repoint_resource(self, subject_id: int, from_id: int):
        """Update the subject resource to remove its relatship from its current aggregate group"""

    def get_all_connected_resources(
        self, id: int | ResourceEntity
    ) -> Sequence[ResourceEntity]:
        """Find all resource ids that either point to or are pointed to by `id`"""


class MembershipRepository(Protocol):
    def get(self, membership_id: int) -> MembershipEntity: ...

    def create(
        self, resource_id: int, source_name: str, source_id: str, active: bool = True
    ) -> ResourceEntity:
        pass

    def repoint_memberships(ids: Sequence[int], to_resource_id: int):
        """Updates all memberships to point to the provided id."""
