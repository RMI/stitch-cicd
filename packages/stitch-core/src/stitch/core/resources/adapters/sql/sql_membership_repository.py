from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from stitch.core.resources.adapters.sql.common import extract_id
from stitch.core.resources.adapters.sql.errors import MembershipIntegrityError
from stitch.core.resources.adapters.sql.model.membership import MembershipModel
from stitch.core.resources.domain.entities import MembershipEntity, ResourceEntity
from stitch.core.resources.domain.ports import MembershipRepository


class SQLMembershipRepository(MembershipRepository):
    _session: Session

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, resource_id: int, source: str, source_pk: str):
        model = MembershipModel(
            resource_id=resource_id,
            source=source,
            source_pk=source_pk,
        )

        self._session.add(model)
        self._session.flush()
        return model.id

    def get(self, membership_id: int) -> MembershipEntity | None:
        model = self._session.get(MembershipModel, membership_id)
        if model is None:
            return None
        return model.as_entity()

    def get_active_members(self, resource_id: int) -> Sequence[MembershipModel]:
        stmt = select(MembershipModel).where(MembershipModel.resource_id == resource_id)

        return self._session.execute(stmt).scalars().all()

    def create_repointed_memberships(
        self,
        from_resources: Sequence[ResourceEntity | int],
        to_resource: ResourceEntity | int,
    ):
        """Create new memberships pointing to a different resource.

        Collect all memberships whose `resource_id` is in the `from_resoure_ids` argument. For each of these, create
        a new membership where `resource_id` = `to_resource_id`.

        This all takes place after a `merge_resources` operation where a new ResourceModel is created.

        Args:
            from_resoure_ids: the original resource_ids
            to_resource_id: the new resource id

        Returns:
            Sequence of newly created `MembershipEntity` objects.
        """
        from_ids = [extract_id(res) for res in from_resources]
        to_id = extract_id(to_resource)
        existing_memberships = self._session.scalars(
            select(MembershipModel).where(MembershipModel.resource_id.in_(from_ids))
        ).all()
        if any((mem.status is not None for mem in existing_memberships)):
            invalid = filter(lambda m: m.status is not None, existing_memberships)
            repr_ = f"({','.join(map(repr, invalid))})"
            raise MembershipIntegrityError(
                f"Cannot repoint memberships that have already been repointed. {repr_}"
            )

        new_memberships = map(
            lambda mem: self.create(
                resource_id=to_id, source=mem.source, source_pk=mem.source_pk
            ),
            existing_memberships,
        )
        self._session.add_all(new_memberships)
        self._session.flush()
        return [m.as_entity() for m in new_memberships]
