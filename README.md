# OpenVPN Config Generator

This project provides a web-based interface for generating OpenVPN server and client configurations. The application is built using Flask and Docker, and it allows users to generate server configurations, client configurations, and client configurations based on an existing server configuration.

## Features

- Generate OpenVPN server configuration
- Generate OpenVPN client configuration
- Generate OpenVPN client configuration from an existing server configuration
- Download configurations as tar archives

## Prerequisites

- Docker
- Docker Compose

## Getting Started

Follow these instructions to get the application up and running on your local machine.

### Clone the Repository

```sh
git clone https://github.com/your-username/openvpn-config-generator.git
cd openvpn-config-generator
docker-compose up --build
```

### Access the Application

Open a web browser and navigate to `http://localhost:5000`. You should see the home page of the application.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## TODO list:
- [ ] Restructure files and dockerfile (start file main.py)
- [ ] Update README.md (add multibuild instructions + other info)
like this:
```bash
# Create a new builder instance
docker buildx create --name=container --driver=docker-container --use --bootstrap

# Build the image (multibuild for amd64 and arm64)
docker buildx build \
  --builder=container \
  --platform=linux/amd64,linux/arm64 \
  -t asirush/openvpn_config_generator:latest \
  --push .
```

- [ ] Add Helm charts for k*s deployment
- [ ] Add CI/CD pipeline for github actions (autobuild and push to dockerhub)
- [ ] Add config file (use os.getenv instead of hardcoded values)
like this:
```python
# config.py file

import os

# Get the value of the environment variable
value = os.getenv('FLASK_SECRET_KEY', 'default_value')
```
