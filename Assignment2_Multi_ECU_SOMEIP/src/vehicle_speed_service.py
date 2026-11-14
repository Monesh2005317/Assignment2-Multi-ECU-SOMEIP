import asyncio
import logging

from someipy import (
    Event,
    EventGroup,
    Method,
    MethodResult,
    MessageType,
    ReturnCode,
    ServiceBuilder,
    TransportLayerProtocol,
    ServerServiceInstance,
    connect_to_someipy_daemon,
)

from someipy.serialization import SomeIpPayload, Uint16, Uint8

from someipy.someipy_logging import set_someipy_log_level

from vehicle_speed_interface import (
    INTERFACE_IP,
    SERVICE_ID,
    INSTANCE_ID,
    PROVIDER_PORT,
    GET_SPEED_METHOD_ID,
    GET_VEHICLE_STATE_METHOD_ID,
    SPEED_CHANGED_EVENT_ID,
    OVERSPEED_WARNING_EVENT_ID,
    SPEED_EVENTGROUP_ID,
    OVERSPEED_EVENTGROUP_ID,
    STOPPED,
    MOVING,
    OVERSPEED_LIMIT,
)


# ----------------------------------
# VEHICLE STATE
# ----------------------------------

current_speed_kmph = 50

speed_sequence = [50, 60, 70, 80, 90, 100, 0]


# ----------------------------------
# PAYLOAD DEFINITIONS
# ----------------------------------

class SpeedPayload(SomeIpPayload):

    def __init__(self, speed=0):
        self.speed = Uint16(speed)


class VehicleStatePayload(SomeIpPayload):

    def __init__(self, state=STOPPED):
        self.state = Uint8(state)


# ----------------------------------
# METHOD 1: GET SPEED
# ----------------------------------

async def get_speed_handler(input_data, addr):

    global current_speed_kmph

    print("\n[VEHICLE ECU] GetSpeed request received")

    result = MethodResult()

    response = SpeedPayload(current_speed_kmph)

    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response.serialize()

    print(f"Current Speed: {current_speed_kmph} km/h")
    print("[VEHICLE ECU] GetSpeed response sent")

    return result


# ----------------------------------
# METHOD 2: GET VEHICLE STATE
# ----------------------------------

async def get_vehicle_state_handler(input_data, addr):

    global current_speed_kmph

    print("\n[VEHICLE ECU] GetVehicleState request received")

    if current_speed_kmph == 0:
        state = STOPPED
        state_name = "STOPPED"
    else:
        state = MOVING
        state_name = "MOVING"

    result = MethodResult()

    response = VehicleStatePayload(state)

    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response.serialize()

    print(f"Vehicle State: {state_name}")
    print("[VEHICLE ECU] GetVehicleState response sent")

    return result


# ----------------------------------
# METHOD DEFINITIONS
# ----------------------------------

get_speed_method = Method(
    id=GET_SPEED_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
    method_handler=get_speed_handler,
)

get_vehicle_state_method = Method(
    id=GET_VEHICLE_STATE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
    method_handler=get_vehicle_state_handler,
)


# ----------------------------------
# EVENT DEFINITIONS
# ----------------------------------

speed_changed_event = Event(
    id=SPEED_CHANGED_EVENT_ID,
    protocol=TransportLayerProtocol.UDP,
)

overspeed_warning_event = Event(
    id=OVERSPEED_WARNING_EVENT_ID,
    protocol=TransportLayerProtocol.UDP,
)


speed_eventgroup = EventGroup(
    id=SPEED_EVENTGROUP_ID,
    events=[speed_changed_event],
)

overspeed_eventgroup = EventGroup(
    id=OVERSPEED_EVENTGROUP_ID,
    events=[overspeed_warning_event],
)


# ----------------------------------
# VEHICLE SPEED SERVICE
# ----------------------------------

vehicle_speed_service = (
    ServiceBuilder()
    .with_service_id(SERVICE_ID)
    .with_major_version(1)
    .with_method(get_speed_method)
    .with_method(get_vehicle_state_method)
    .with_eventgroup(speed_eventgroup)
    .with_eventgroup(overspeed_eventgroup)
    .build()
)


# ----------------------------------
# SPEED SIMULATION
# ----------------------------------

async def speed_simulation(service_instance):

    global current_speed_kmph

    while True:

        for speed in speed_sequence:

            current_speed_kmph = speed

            print("\n================================")
            print(f"[VEHICLE ECU] Speed: {speed} km/h")
            print("================================")

            # Generate SpeedChanged event
            speed_payload = SpeedPayload(speed)

            service_instance.send_event(
                SPEED_EVENTGROUP_ID,
                SPEED_CHANGED_EVENT_ID,
                speed_payload.serialize(),
            )

            print("[EVENT] SpeedChanged generated")

            # Generate OverspeedWarning only above 80
            if speed > OVERSPEED_LIMIT:

                warning_payload = SpeedPayload(speed)

                service_instance.send_event(
                    OVERSPEED_EVENTGROUP_ID,
                    OVERSPEED_WARNING_EVENT_ID,
                    warning_payload.serialize(),
                )

                print("[EVENT] OVERSPEED WARNING generated")

            await asyncio.sleep(3)


# ----------------------------------
# MAIN VEHICLE ECU APPLICATION
# ----------------------------------

async def main():

    set_someipy_log_level(logging.INFO)

    print("\n================================")
    print("       VEHICLE ECU STARTED")
    print("================================")

    daemon = await connect_to_someipy_daemon()

    service_instance = ServerServiceInstance(
        daemon=daemon,
        service=vehicle_speed_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=PROVIDER_PORT,
        ttl=5,
        cyclic_offer_delay_ms=2000,
    )

    await service_instance.start_offer()

    print("\nVehicleSpeedService AVAILABLE")
    print(f"Service ID: 0x{SERVICE_ID:04X}")
    print(f"Instance ID: 0x{INSTANCE_ID:04X}")

    try:
        await speed_simulation(service_instance)

    finally:

        await service_instance.stop_offer()
        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nVehicle ECU stopped.")
