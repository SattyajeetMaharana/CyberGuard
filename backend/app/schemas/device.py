from uuid import UUID

from pydantic import BaseModel, Field


class DeviceCreate(BaseModel):
    device_identifier: str = Field(min_length=1, max_length=512)
    device_name: str | None = Field(default=None, max_length=200)
    platform: str | None = Field(default=None, max_length=100)


class DeviceResponse(BaseModel):
    id: UUID
    user_id: UUID
    device_name: str | None = None
    platform: str | None = None
    is_active: bool

    model_config = {
        "from_attributes": True,
    }


class DeviceActivationRequest(BaseModel):
    is_active: bool
