from someipy import (
    Event,
    EventGroup,
    Method,
    ServiceBuilder,
    TransportLayerProtocol,
)

from someipy.serialization import SomeIpPayload, Uint8, Uint16


# Network Configuration
INTERFACE_IP = "127.0.0.1"

PROVIDER_PORT = 3000
CONSUMER_PORT = 3002


# VehicleSpeedService Configuration
SERVICE_ID = 0x1234
INSTANCE_ID = 0x5678
MAJOR_VERSION = 1

# Method IDs
GET_SPEED_METHOD_ID = 0x0001
GET_VEHICLE_STATE_METHOD_ID = 0x0002

# Event IDs
SPEED_CHANGED_EVENT_ID = 0x8001
OVERSPEED_WARNING_EVENT_ID = 0x8002

# Event Group IDs
SPEED_EVENTGROUP_ID = 0x0001
OVERSPEED_EVENTGROUP_ID = 0x0002


# Vehicle State
STOPPED = 0
MOVING = 1

OVERSPEED_LIMIT = 80


# Payload: Vehicle Speed (uint16)
class SpeedPayload(SomeIpPayload):

    def __init__(self, speed_kmph=0):
        self.speed_kmph = Uint16(speed_kmph)


# Payload: Vehicle State (uint8)
class VehicleStatePayload(SomeIpPayload):

    def __init__(self, state=STOPPED):
        self.state = Uint8(state)


# Method Definitions
get_speed_method = Method(
    id=GET_SPEED_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)

get_vehicle_state_method = Method(
    id=GET_VEHICLE_STATE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)


# Event Definitions
speed_changed_event = Event(
    id=SPEED_CHANGED_EVENT_ID,
    protocol=TransportLayerProtocol.UDP,
)

overspeed_warning_event = Event(
    id=OVERSPEED_WARNING_EVENT_ID,
    protocol=TransportLayerProtocol.UDP,
)


# Event Groups
speed_eventgroup = EventGroup(
    id=SPEED_EVENTGROUP_ID,
    events=[speed_changed_event],
)

overspeed_eventgroup = EventGroup(
    id=OVERSPEED_EVENTGROUP_ID,
    events=[overspeed_warning_event],
)


# VehicleSpeedService Definition
vehicle_speed_service = (
    ServiceBuilder()
    .with_service_id(SERVICE_ID)
    .with_major_version(MAJOR_VERSION)
    .with_method(get_speed_method)
    .with_method(get_vehicle_state_method)
    .with_eventgroup(speed_eventgroup)
    .with_eventgroup(overspeed_eventgroup)
    .build()
)

