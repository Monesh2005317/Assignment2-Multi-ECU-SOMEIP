# Multi-ECU Service-Oriented Communication Using SOME/IP

## Project Overview

This project demonstrates service-oriented communication between multiple Electronic Control Units (ECUs) using the SOME/IP protocol.

The system is developed using Python and the `someipy` library on Ubuntu Linux. It consists of four independent ECU applications communicating through a SOME/IP daemon.

## System Architecture

The project consists of four ECUs:

### 1. Vehicle ECU
- Acts as a provider of VehicleSpeedService.
- Implements `GetSpeed()` and `GetVehicleState()` methods.
- Publishes `SpeedChanged` events.
- Publishes `OverspeedWarning` events when vehicle speed exceeds 80 km/h.

### 2. Instrument Cluster ECU
- Acts as a consumer of VehicleSpeedService.
- Calls `GetSpeed()` and `GetVehicleState()`.
- Subscribes to speed and overspeed events.

### 3. Climate ECU
- Acts as a provider of ClimateService.
- Implements `GetCabinTemperature()` and `SetTargetTemperature()`.
- Publishes `CabinTemperatureChanged` events.
- Validates target temperature requests between 16°C and 30°C.

### 4. Central Display ECU
- Consumes both VehicleSpeedService and ClimateService.
- Displays vehicle speed, vehicle state and cabin temperature.
- Sends target temperature requests.
- Subscribes to all three events.

## Technologies Used

- Python 3
- SOME/IP
- someipy 2.1.2
- Ubuntu Linux
- UDP Communication
- Wireshark

## Project Structure

```text
Assignment2-Multi-ECU-SOMEIP/
│
├── src/
│   ├── vehicle_speed_interface.py
│   ├── vehicle_speed_service.py
│   ├── cluster_client.py
│   ├── climate_interface.py
│   ├── climate_service.py
│   ├── central_display.py
│   └── temperature_validation_test.py
│
├── captures/
├── screenshots/
├── docs/
│   └── Project_Report.docx
│
├── README.md
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/Assignment2-Multi-ECU-SOMEIP.git
cd Assignment2-Multi-ECU-SOMEIP
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependency:

```bash
pip install someipy==2.1.2
```

## Running the Project

Run each application in a separate terminal.

### Terminal 1: SOME/IP Daemon

```bash
someipyd
```

### Terminal 2: Vehicle ECU

```bash
source .venv/bin/activate
PYTHONPATH=src python src/vehicle_speed_service.py
```

### Terminal 3: Climate ECU

```bash
source .venv/bin/activate
PYTHONPATH=src python src/climate_service.py
```

### Terminal 4: Instrument Cluster ECU

```bash
source .venv/bin/activate
PYTHONPATH=src python src/cluster_client.py
```

### Terminal 5: Central Display ECU

```bash
source .venv/bin/activate
PYTHONPATH=src python src/central_display.py
```

## Temperature Validation

Run the validation client while the SOME/IP daemon and Climate ECU are running:

```bash
source .venv/bin/activate
PYTHONPATH=src python src/temperature_validation_test.py
```

### Validation Results

| Input | Expected Result | Observed Result |
|---|---|---|
| 16°C | ACCEPTED | ACCEPTED |
| 30°C | ACCEPTED | ACCEPTED |
| 10°C | INVALID_TEMPERATURE | INVALID_TEMPERATURE |
| 35°C | INVALID_TEMPERATURE | INVALID_TEMPERATURE |

## Testing and Results

The following functionality was demonstrated:

- Successful SOME/IP daemon startup.
- VehicleSpeedService discovery.
- ClimateService discovery.
- Request-response communication.
- Event-based communication.
- Overspeed warning above 80 km/h.
- Multiple consumers accessing VehicleSpeedService.
- Central Display consuming two independent services.
- Temperature range validation.
- Communication resuming after Climate ECU restart.

## Screenshots and Documentation

- `screenshots/` contains execution screenshots.
- `docs/Project_Report.docx` contains the detailed project report.
- `captures/` is reserved for network packet captures. A complete method/event packet capture was not included.

## Learning Outcomes

- Understanding SOME/IP architecture.
- Implementing service discovery.
- Implementing service providers and consumers.
- Implementing request-response methods.
- Implementing publish-subscribe event communication.
- Understanding multi-ECU communication.
- Implementing parameter validation and error handling.

## Author

**Monesh M. Borole**

Electronics and Telecommunication Engineering  
AISSMS Institute of Information Technology, Pune
