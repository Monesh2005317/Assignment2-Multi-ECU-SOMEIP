import asyncio
import logging

from someipy import (
    Method,
    MethodResult,
    MessageType,
    ReturnCode,
    ServiceBuilder,
    ServerServiceInstance,
    TransportLayerProtocol,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level

from climate_interface import (
    INTERFACE_IP,
    CLIMATE_SERVICE_ID,
    CLIMATE_INSTANCE_ID,
    PROVIDER_PORT,
    GET_CABIN_TEMPERATURE_METHOD_ID,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    CABIN_TEMPERATURE_EVENTGROUP_ID,
    MIN_TARGET_TEMPERATURE,
    MAX_TARGET_TEMPERATURE,
    ACCEPTED,
    INVALID_TEMPERATURE,
    TemperaturePayload,
    TargetTemperaturePayload,
    TemperatureStatusPayload,
    cabin_temperature_changed_event,
    cabin_temperature_eventgroup,
)


# ----------------------------------
# CLIMATE ECU STATE
# ----------------------------------

current_temperature = 240
target_temperature = 220

temperature_sequence = [240, 245, 250, 255, 260]


# ----------------------------------
# METHOD 1: GET CABIN TEMPERATURE
# ----------------------------------

async def get_temperature_handler(input_data, addr):

    global current_temperature

    print("\n[CLIMATE ECU] GetCabinTemperature request received")

    result = MethodResult()

    response = TemperaturePayload(current_temperature)

    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response.serialize()

    print(
        f"Cabin Temperature: {current_temperature / 10:.1f} °C"
    )

    return result


# ----------------------------------
# METHOD 2: SET TARGET TEMPERATURE
# ----------------------------------

async def set_target_temperature_handler(input_data, addr):

    global target_temperature

    print("\n[CLIMATE ECU] SetTargetTemperature request received")

    request = TargetTemperaturePayload()
    request.deserialize(input_data)

    requested_temperature = request.temperature.value

    print(
        f"Requested Temperature: {requested_temperature / 10:.1f} °C"
    )

    if MIN_TARGET_TEMPERATURE <= requested_temperature <= MAX_TARGET_TEMPERATURE:

        target_temperature = requested_temperature
        status = ACCEPTED

        print("Status: ACCEPTED")

    else:

        status = INVALID_TEMPERATURE

        print("Status: INVALID_TEMPERATURE")
        print("Target temperature remains unchanged.")

    result = MethodResult()

    response = TemperatureStatusPayload(status)

    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response.serialize()

    return result


# ----------------------------------
# METHOD DEFINITIONS
# ----------------------------------

get_temperature_method = Method(
    id=GET_CABIN_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
    method_handler=get_temperature_handler,
)

set_temperature_method = Method(
    id=SET_TARGET_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
    method_handler=set_target_temperature_handler,
)


# ----------------------------------
# CLIMATE SERVICE
# ----------------------------------

climate_service = (
    ServiceBuilder()
    .with_service_id(CLIMATE_SERVICE_ID)
    .with_major_version(1)
    .with_method(get_temperature_method)
    .with_method(set_temperature_method)
    .with_eventgroup(cabin_temperature_eventgroup)
    .build()
)


# ----------------------------------
# TEMPERATURE SIMULATION
# ----------------------------------

async def temperature_simulation(service_instance):

    global current_temperature

    while True:

        for temperature in temperature_sequence:

            current_temperature = temperature

            print("\n================================")
            print(
                f"[CLIMATE ECU] Cabin Temperature: {temperature / 10:.1f} °C"
            )
            print("================================")

            payload = TemperaturePayload(temperature)

            service_instance.send_event(
                CABIN_TEMPERATURE_EVENTGROUP_ID,
                CABIN_TEMPERATURE_CHANGED_EVENT_ID,
                payload.serialize(),
            )

            print("[EVENT] CabinTemperatureChanged generated")

            await asyncio.sleep(4)


# ----------------------------------
# MAIN CLIMATE ECU
# ----------------------------------

async def main():

    set_someipy_log_level(logging.INFO)

    print("\n================================")
    print("        CLIMATE ECU STARTED")
    print("================================")

    daemon = await connect_to_someipy_daemon()

    service_instance = ServerServiceInstance(
        daemon=daemon,
        service=climate_service,
        instance_id=CLIMATE_INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=PROVIDER_PORT,
        ttl=5,
        cyclic_offer_delay_ms=2000,
    )

    await service_instance.start_offer()

    print("\nClimateService AVAILABLE")
    print(f"Service ID: 0x{CLIMATE_SERVICE_ID:04X}")
    print(f"Instance ID: 0x{CLIMATE_INSTANCE_ID:04X}")

    try:

        await temperature_simulation(service_instance)

    finally:

        await service_instance.stop_offer()
        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nClimate ECU stopped.")
