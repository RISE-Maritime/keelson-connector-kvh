# Keelson Connector KVH

Tools for connecting KVH IMU units to the Keelson ecosystem. This connector supports KVH IMU binary output format C (default as per OpenDLV implementation).

## KVH IMU Binary Format C

The connector processes 38-byte binary messages with the following structure:

- **Header** (bytes 1-4): Always `0xFE81FF57`
- **Message Data** (bytes 5-34):
  - X,Y,Z rotational data (rad/s) - SPFP format
  - X,Y,Z acceleration data (g's, converted to m/s²) - SPFP format
  - Interleaved Temperature/Magnetic data - SPFP format
  - Status byte (sensor validity flags)
  - Sequence number (0-127) - UINT8
- **CRC** (bytes 35-38): CRC-32/MPEG-2 checksum (split as 2x UINT16)

### Interleaved Temperature/Magnetic Data
Based on sequence number modulo 4:
- **sequence % 4 == 0**: Temperature (°C)
- **sequence % 4 == 1**: Magnetic field X (Gauss)
- **sequence % 4 == 2**: Magnetic field Y (Gauss)  
- **sequence % 4 == 3**: Magnetic field Z (Gauss)

## Quick Start

```bash
# Serial connection via socat

socat -d -d -v OPEN:/dev/cu.usbserial-FT0R4P590,rdonly,nonblock=1,ignoreeof STDOUT | bin/main --log-level 10 -r rise -e storakrabban --publish raw --publish imu --publish pos

socat /dev/ttyUSB0,b115200,raw,echo=0 - | 




socat /dev/ttyUSB4,b921600,raw,echo=0 - | bin/main --log-level 10 -r rise -e storakrabban --publish raw --publish imu --publish pos

docker run -ti --init --rm --net=host --device=/dev/ttyUSB4 registry.opendlv.org/community/opendlv-device-imu-kvhp1775:local --cid=111 --debug --port=/dev/ttyUSB4 --messageType=C


socat /dev/ttyUSB0,b115200,raw,echo=0 - | bin/main --log-level 10 -r rise -e kvh_imu --publish raw --publish imu

# With frame ID for coordinate reference
socat /dev/ttyUSB0,b115200,raw,echo=0 - | bin/main --log-level 10 -r rise -e kvh_imu --publish imu --frame-id "imu_link"
```

## Published Topics

- **raw_json**: Raw binary data as hex strings (if `--publish raw`)
- **linear_acceleration_mpss**: 3D acceleration vectors in m/s² (if `--publish imu`)
- **angular_velocity_radps**: 3D angular velocity vectors in rad/s (if `--publish imu`)

## Status Monitoring

The connector tracks and logs IMU message frequency every 5 seconds for monitoring purposes.

---

## Legacy Documentation 



```

## Record Data with Keelson MCAP

```bash

sudo docker run --rm --network host  --name mcap-logger --volume ~/rec:/rec ghcr.io/rise-maritime/keelson:0.3.7-pre.51 "keelson_processor_ais --output_path rec -k rise/v0/landkrabban/**"

```

 --mode client --connect tcp/10.10.7.2:7448


Setup for development environment on your own computer: ´

1) Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - Docker desktop will provide you with an UI ´´for monitoring and controlling docker containers and images along debugging 
   - If you want to learn more about docker and its building blocks of images and containers checkout [Docker quick hands-on in guide](https://docs.docker.com/guides/get-started/)
2) Start up of **Zenoh router** either in your computer or any other computer within your local network 

   ```bash
    # Navigate to folder containing docker-compose.zenoh-router.yml
  
    # Start router with log output 
    docker-compose -f containing docker-compose.zenoh-router.yml up 

    # If no obvious errors, stop container "ctrl-c"

    # Start container and let it run in the background/detached (append -d) 
    docker-compose -f containing docker-compose.zenoh-router.yml up -d
   ```

    [Link to --> docker-compose.zenoh-router.yml](docker-compose.zenoh-router.yml)

1) Now the Zenoh router is hopefully running in the background and should be available on localhost:8000. This can be example tested with [Zenoh Rest API ](https://zenoh.io/docs/apis/rest/) or continue to next step running Python API
2) Set up python virtual environment  `python >= 3.11`
   1) Install package `pip install -r requirements.txt`
3)  Now you are ready to explore some example scripts in the [exploration folder](./exploration/) 
    1)  Sample are coming from:
         -   [Zenoh Python API ](https://zenoh-python.readthedocs.io/en/0.10.1-rc/#quick-start-examples)


[Zenoh CLI for debugging and problem solving](https://github.com/RISE-Maritime/zenoh-cli)




UDP 1830 



## Start UDP AIS stream on port 1830

Step 1: Set up configuration file

- Make a folder for Keelson connectors and processors:
  - Copy a docker compose file [docker-compose.ais-processor.yml](./docker-compose.ais-processor.yml) OR create a file with name "docker-compose.ais-processor.yml" and add content bellow 

```yml
services:

  keelson-processor-ais:
    image: ghcr.io/rise-maritime/keelson-processor-ais:latest
    container_name: keelson-processor-ais
    restart: unless-stopped
    network_mode: "host"
    command: "--log-level 10 --publish udp_sjv --subscribe sjofartsverket"
```

Step 2: Set up docker service configuration

- Open a terminal and navigate to location where you created the file
- Run following start up command in a terminal to start the service
  
  ```bash
  docker compose -f docker-compose.ais-processor.yml up -d
  ```

- Docker images will be downloaded and service started 

Step 3: Open Docker Desktop

- Check if you can find the new service in docker desktop
- From now on you can start and stop the service from docker desktop (You do not need to do the step 2 again)  
