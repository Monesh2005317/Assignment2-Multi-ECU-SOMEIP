import asyncio
import logging

from someipy import (
    ClientServiceInstance,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level

from vehicle_speed_interface import (
    INTERFACE_IP,
    CONSUMER_PORT,
    SERVICE_ID,
    INSTANCE_ID,
    GET_SPEED_METHOD_ID,
    GET_VEHICLE_STATE_METHOD_ID,
    SPEED_CHANGED_EVENT_ID,
    OVERSPEED_WARNING_EVENT_ID,
    SpeedPayload,
    VehicleStatePayload,
    speed_eventgroup,
    overspeed_eventgroup,
    vehicle_speed_service,
)


# ----------------------------------
# EVENT CALLBACK
# ----------------------------------

def speed_event_callback(event_id, payload):

    if event_id == SPEED_CHANGED_EVENT_ID:

        speed = SpeedPayload().deserialize(payload)

        print("\n[INSTRUMENT CLUSTER]")
        print("SpeedChanged notification received")
        print(f"Vehicle Speed: {speed.speed_kmph.value} km/h")

    elif event_id == OVERSPEED_WARNING_EVENT_ID:

        speed = SpeedPayload().deserialize(payload)

        print("\n!!! OVERSPEED WARNING !!!")
        print(f"Vehicle Speed: {speed.speed_kmph.value} km/h")


# ----------------------------------
# INSTRUMENT CLUSTER APPLICATION
# ----------------------------------

async def main():

    set_someipy_log_level(logging.INFO)

    print("\n====================================")
    print("       INSTRUMENT CLUSTER ECU")
    print("====================================")

    daemon = await connect_to_someipy_daemon()

    client_instance = ClientServiceInstance(
        daemon=daemon,
        service=vehicle_speed_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=CONSUMER_PORT,
    )

    # Register event callback
    client_instance.register_callback(speed_event_callback)

    print("\nSearching for VehicleSpeedService...")

    # Wait for service availability
    while not await client_instance.is_available():

        print("Waiting for Vehicle ECU...")
        await asyncio.sleep(1)

    print("\nVehicleSpeedService AVAILABLE")

    # ----------------------------------
    # SUBSCRIBE TO EVENTS
    # ----------------------------------

    client_instance.subscribe_eventgroup(
        speed_eventgroup,
        5,
    )

    client_instance.subscribe_eventgroup(
        overspeed_eventgroup,
        5,
    )

    print("Subscribed to SpeedChanged")
    print("Subscribed to OverspeedWarning")

    await asyncio.sleep(1)

    # ----------------------------------
    # CALL GET SPEED
    # ----------------------------------

    speed_result = await client_instance.call_method(
        GET_SPEED_METHOD_ID,
        b"",
    )

    speed = SpeedPayload().deserialize(speed_result.payload)

    print("\n[GET SPEED RESPONSE]")
    print(f"Vehicle Speed: {speed.speed_kmph.value} km/h")

    # ----------------------------------
    # CALL GET VEHICLE STATE
    # ----------------------------------

    state_result = await client_instance.call_method(
        GET_VEHICLE_STATE_METHOD_ID,
        b"",
    )

    state = VehicleStatePayload().deserialize(
        state_result.payload
    )

    state_name = (
        "STOPPED" if state.state.value == 0 else "MOVING"
    )

    print("\n[GET VEHICLE STATE RESPONSE]")
    print(f"Vehicle State: {state_name}")

    # Keep ECU running for event reception
    print("\nInstrument Cluster ECU running...")

    try:
        await asyncio.Future()

    finally:
        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nInstrument Cluster ECU stopped.")
