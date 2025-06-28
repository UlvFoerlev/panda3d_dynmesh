from pydantic import BaseModel


class DynMeshSettings(BaseModel):
    floating_point_precision: int | None = None
