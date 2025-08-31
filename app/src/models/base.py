from uuid import UUID

from pydantic import BaseModel, Field, validator


class UUIDBase(BaseModel):
    uuid: UUID = Field(alias='id')

    @validator('uuid', pre=True)
    def parse_uuid(cls, v):
        if isinstance(v, UUID):
            return v
        if isinstance(v, str):
            try:
                return UUID(v)
            except ValueError:
                raise ValueError(f'Invalid UUID string: {v}')
        raise TypeError('uuid must be a UUID instance or a valid UUID string')

    model_config = {
        "populate_by_name": True
    }
