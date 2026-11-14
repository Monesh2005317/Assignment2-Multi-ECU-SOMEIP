import asyncio

from someipy import ClientServiceInstance, connect_to_someipy_daemon

from climate_interface import (
    INTERFACE_IP,
    CLIMATE_INSTANCE_ID,
    CONSUMER_PORT,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    TargetTemperaturePayload,
    TemperatureStatusPayload,
    climate_service,
)


async def main():

    daemon = await connect_to_someipy_daemon()

    client = ClientServiceInstance(
        daemon=daemon,
        service=climate_service,
        instance_id=CLIMATE_INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=3003,
    )

    try:

        print("Searching for ClimateService...")

        while not await client.is_available():
            await asyncio.sleep(1)

        print("ClimateService AVAILABLE\n")

        test_values = [160, 300, 100, 350]

        for temperature in test_values:

            request = TargetTemperaturePayload(temperature)

            result = await client.call_method(
                SET_TARGET_TEMPERATURE_METHOD_ID,
                request.serialize(),
            )

            response = TemperatureStatusPayload().deserialize(
                result.payload
            )

            status = (
                "ACCEPTED"
                if response.status.value == 0
                else "INVALID_TEMPERATURE"
            )

            print(
                f"Input: {temperature / 10:.1f} °C "
                f"| Expected: "
                f"{'ACCEPTED' if temperature in [160, 300] else 'INVALID_TEMPERATURE'} "
                f"| Actual: {status}"
            )

            await asyncio.sleep(1)

    finally:
        await daemon.disconnect_from_daemon()


if __name__ == "__main__":
    asyncio.run(main())
