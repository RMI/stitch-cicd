from collections.abc import Sequence
from sqlalchemy.orm import Session

from stitch.core.resources.adapters.sql.common import extract_id
from stitch.core.resources.adapters.sql.errors import (
    EntityNotFoundError,
    ResourceIntegrityError,
)
from .model.resource import ResourceModel
from stitch.core.resources.domain.entities import (
    ResourceEntity,
    UserPlaceholder,
)
from stitch.core.resources.domain.ports import ResourceRepository


class SQLResourceRepository(ResourceRepository):
    _session: Session

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        repointed_to: int | None = None,
        name: str | None = None,
        country: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        created_by: UserPlaceholder | None = None,
    ) -> int:
        model = ResourceModel.create(
            repointed_to=repointed_to,
            name=name,
            country=country,
            latitude=latitude,
            longitude=longitude,
        )
        self._session.add(model)
        self._session.flush()
        return model.id

    def get(self, resource_id: int) -> ResourceEntity | None:
        model = self._session.get(ResourceModel, resource_id)
        if model is None:
            return None
        return model.as_entity()

    def merge_resources(
        self,
        left: ResourceEntity | int,
        right: ResourceEntity | int,
    ) -> ResourceEntity:
        """Merge two resources and repoint them to the newly created resource.

        Merging constraints:
        * the ids/entities are not the same
        * both resource exist in the db
        * neither has been repointed already

        Args:
            left: an unmerged resource
            right: an unmerged resource

        Returns:
            The new resource pointed to by the passed entities.

        Raises:
            ResourceIntegrityError: If ids are the same or if either has been repointed
            EntityNotFoundError: If either `Resource` hasn't been persisted
        """
        left_id = extract_id(left)
        right_id = extract_id(right)
        if left_id == right_id:
            raise ResourceIntegrityError(
                f"Cannot merge Resources with same id. ({left_id} == {right_id})"
            )
        left_model = self._session.get(ResourceModel, left_id)
        right_model = self._session.get(ResourceModel, right_id)
        if left_model is None or right_model is None:
            nulls = filter(
                lambda x: x,
                (
                    None if left_model is not None else str(left_id),
                    None if right_model is not None else str(right_id),
                ),
            )
            raise EntityNotFoundError(f"No Resource foun for ({','.join(nulls)})")

        if left_model.repointed_to or right_model.repointed_to:
            msg = f"left: (id: {left_id}, repointed_to:  {left_model.repointed_to}), "
            msg += f"right: (id: {right_id}, repointed_to: {right_model.repointed_to})"
            raise ResourceIntegrityError(
                f"Cannot merge any resource that has already been merged. {msg}"
            )

        # once here, both Resources exist and neither has been repointed
        # NOTE: We create an essentially empty resource. Determining which source data are used
        # to create the final aggregate resource representation will be handled in a domain-specific
        # component or view/presentation layer
        new_resource = ResourceModel.create(
            repointed_to=None,
            created_by="user",
        )
        self._session.add(new_resource)
        self._session.flush()
        left_model.repointed_to = new_resource.id
        right_model.repointed_to = new_resource.id
        self._session.add_all((left_model, right_model))
        return new_resource.as_entity()

    def get_root_resource(self, resource_id: int):
        """Trace the `repointed_to` values until reaching a `ResourceModel` where  repointed_to is None/null"""
        pass

    def repoint_resource(self, resource_id: int, to_resource_id: int):
        """
        Update the resource's `repointed_to`  to `to_resource_id`
        """
