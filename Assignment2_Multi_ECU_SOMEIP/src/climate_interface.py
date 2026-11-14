from someipy import (
    Event,
    EventGroup,
    Method,
    ServiceBuilder,
    TransportLayerProtocol,
)

from someipy.serialization import SomeIpPayload, Sint16, Uint8


# Network Configuration
INTERFACE_IP = "127.0.0.1"

PROVIDER_PORT = 3001
CONSUMER_PORT = 3003


# Climate Service Configuration
CLIMATE_SERVICE_ID = 0x2234
CLIMATE_INSTANCE_ID = 0x0001
CLIMATE_MAJOR_VERSION = 1


# Method IDs
GET_CABIN_TEMPERATURE_METHOD_ID = 0x0001
SET_TARGET_TEMPERATURE_METHOD_ID = 0x0002


# Event IDs
CABIN_TEMPERATURE_CHANGED_EVENT_ID = 0x8001

# Event Group ID
CABIN_TEMPERATURE_EVENTGROUP_ID = 0x0001


# Temperature Limits
MIN_TARGET_TEMPERATURE = 160
MAX_TARGET_TEMPERATURE = 300


# Response Status
ACCEPTED = 0
INVALID_TEMPERATURE = 1


# Temperature Payload
class TemperaturePayload(SomeIpPayload):

    def __init__(self, temperature=240):
        self.temperature = Sint16(temperature)


# Target Temperature Request
class TargetTemperaturePayload(SomeIpPayload):

    def __init__(self, temperature=220):
        self.temperature = Sint16(temperature)


# Response Status Payload
class TemperatureStatusPayload(SomeIpPayload):

    def __init__(self, status=ACCEPTED):
        self.status = Uint8(status)


# Methods
get_cabin_temperature_method = Method(
    id=GET_CABIN_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)

set_target_temperature_method = Method(
    id=SET_TARGET_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)


# Event
cabin_temperature_changed_event = Event(
    id=CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    protocol=TransportLayerProtocol.UDP,
)


# Event Group
cabin_temperature_eventgroup = EventGroup(
    id=CABIN_TEMPERATURE_EVENTGROUP_ID,
    events=[cabin_temperature_changed_event],
)


# Climate Service
climate_service = (
    ServiceBuilder()
    .with_service_id(CLIMATE_SERVICE_ID)
    .with_major_version(CLIMATE_MAJOR_VERSION)
    .with_method(get_cabin_temperature_method)
    .with_method(set_target_temperature_method)
    .with_eventgroup(cabin_temperature_eventgroup)
    .build()
)
