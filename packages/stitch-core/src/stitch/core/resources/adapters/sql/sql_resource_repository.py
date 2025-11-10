from typing import Any

from sqlalchemy.orm import Session
from .model.resource import ResourceModel
from stitch.core.resources.domain.entities import ResourceEntity
from stitch.core.resources.domain.ports import ResourceRepository


def normalize_resource_model(model: ResourceModel) -> dict[str, Any]:
    """Translate provider-specific ORM row into the normalized dict expected by domain."""
    projection = {
        "id": model.id,
        "source": model.source,
        "source_pk": model.source_pk,
        "repointed_to": model.repointed_to,
        "name": model.name,
        "country": model.country,
        "operator": model.operator,
        "latitude": float(model.latitude) if model.latitude is not None else None,
        "longitude": float(model.longitude) if model.longitude is not None else None,
        "created": model.created,
    }
    return projection


class SQLResourceRepository(ResourceRepository):
    _session: Session

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        repointed_to: int | None = None,
        name: str | None = None,
        country: str | None = None,
        operator: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> int:
        model = ResourceModel.create(
            repointed_to=repointed_to,
            name=name,
            country=country,
            operator=operator,
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

    def get_root_resource(self, resource_id: int):
        """Trace the `repointed_to` values until reaching a `ResourceModel` where  repointed_to is None/null"""
        pass

    def repoint_resource(self, resource_id: int, to_resource_id: int):
        """
        Update the resource's `repointed_to`  to `to_resource_id`
        """

    def _model_to_entity(self, model: ResourceModel):
        return ResourceEntity(**normalize_resource_model(model))
