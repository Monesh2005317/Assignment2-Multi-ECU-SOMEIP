import asyncio
import logging

from someipy import (
    ClientServiceInstance,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level

# Vehicle interface
from vehicle_speed_interface import (
    INTERFACE_IP,
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

# Climate interface
from climate_interface import (
    CLIMATE_SERVICE_ID,
    CLIMATE_INSTANCE_ID,
    GET_CABIN_TEMPERATURE_METHOD_ID,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    TemperaturePayload,
    TargetTemperaturePayload,
    TemperatureStatusPayload,
    cabin_temperature_eventgroup,
    climate_service,
)


# Central Display network ports
VEHICLE_CLIENT_PORT = 3004
CLIMATE_CLIENT_PORT = 3005

TARGET_TEMPERATURE = 220


# ==================================
# VEHICLE EVENT CALLBACK
# ==================================

def vehicle_event_callback(event_id, payload):

    if event_id == SPEED_CHANGED_EVENT_ID:

        speed = SpeedPayload().deserialize(payload)

        print(
            f"\n[DISPLAY] Vehicle Speed Updated: "
            f"{speed.speed_kmph.value} km/h"
        )

    elif event_id == OVERSPEED_WARNING_EVENT_ID:

        speed = SpeedPayload().deserialize(payload)

        print("\n!!! OVERSPEED WARNING !!!")
        print(f"Vehicle Speed: {speed.speed_kmph.value} km/h")


# ==================================
# CLIMATE EVENT CALLBACK
# ==================================

def climate_event_callback(event_id, payload):

    if event_id == CABIN_TEMPERATURE_CHANGED_EVENT_ID:

        temperature = TemperaturePayload().deserialize(payload)

        print(
            f"\n[DISPLAY] Cabin Temperature Updated: "
            f"{temperature.temperature.value / 10:.1f} °C"
        )


# ==================================
# VEHICLE SERVICE CONSUMPTION
# ==================================

async def consume_vehicle_service(client):

    print("\nSearching for VehicleSpeedService...")

    while not await client.is_available():
        await asyncio.sleep(1)

    print("\nVehicleSpeedService : AVAILABLE")

    client.subscribe_eventgroup(speed_eventgroup, 5)
    client.subscribe_eventgroup(overspeed_eventgroup, 5)

    print("Subscribed to SpeedChanged")
    print("Subscribed to OverspeedWarning")

    await asyncio.sleep(1)

    # GetSpeed
    speed_result = await client.call_method(
        GET_SPEED_METHOD_ID,
        b"",
    )

    speed = SpeedPayload().deserialize(speed_result.payload)

    print(f"\nVehicle Speed: {speed.speed_kmph.value} km/h")

    # GetVehicleState
    state_result = await client.call_method(
        GET_VEHICLE_STATE_METHOD_ID,
        b"",
    )

    state = VehicleStatePayload().deserialize(state_result.payload)

    state_name = "STOPPED" if state.state.value == 0 else "MOVING"

    print(f"Vehicle State: {state_name}")


# ==================================
# CLIMATE SERVICE CONSUMPTION
# ==================================

async def consume_climate_service(client):

    print("\nSearching for ClimateService...")

    while not await client.is_available():
        await asyncio.sleep(1)

    print("\nClimateService : AVAILABLE")

    client.subscribe_eventgroup(
        cabin_temperature_eventgroup,
        5,
    )

    print("Subscribed to CabinTemperatureChanged")

    await asyncio.sleep(1)

    # GetCabinTemperature
    temperature_result = await client.call_method(
        GET_CABIN_TEMPERATURE_METHOD_ID,
        b"",
    )

    temperature = TemperaturePayload().deserialize(
        temperature_result.payload
    )

    print(
        f"\nCabin Temperature: "
        f"{temperature.temperature.value / 10:.1f} °C"
    )

    # SetTargetTemperature
    request = TargetTemperaturePayload(TARGET_TEMPERATURE)

    result = await client.call_method(
        SET_TARGET_TEMPERATURE_METHOD_ID,
        request.serialize(),
    )

    status = TemperatureStatusPayload().deserialize(
        result.payload
    )

    if status.status.value == 0:
        print("Target Temperature: 22.0 °C")
        print("Temperature Status: ACCEPTED")
    else:
        print("Temperature Status: INVALID_TEMPERATURE")


# ==================================
# MAIN CENTRAL DISPLAY
# ==================================

async def main():

    set_someipy_log_level(logging.INFO)

    print("\n==========================================")
    print("          CENTRAL VEHICLE DISPLAY")
    print("==========================================")

    daemon = await connect_to_someipy_daemon()

    # Vehicle Service Client
    vehicle_client = ClientServiceInstance(
        daemon=daemon,
        service=vehicle_speed_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=VEHICLE_CLIENT_PORT,
    )

    vehicle_client.register_callback(vehicle_event_callback)

    # Climate Service Client
    climate_client = ClientServiceInstance(
        daemon=daemon,
        service=climate_service,
        instance_id=CLIMATE_INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=CLIMATE_CLIENT_PORT,
    )

    climate_client.register_callback(climate_event_callback)

    try:

        print("\nVehicleSpeedService : WAITING")
        print("ClimateService      : WAITING")

        await asyncio.gather(
            consume_vehicle_service(vehicle_client),
            consume_climate_service(climate_client),
        )

        await asyncio.Future()

    finally:

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nCentral Display ECU stopped.")
