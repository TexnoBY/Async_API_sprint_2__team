from uuid import UUID

from pydantic import BaseModel, Field, field_validator



class UUIDBase(BaseModel):
    uuid: UUID = Field(alias='id')

    @field_validator('uuid', mode='before')
    @classmethod
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
