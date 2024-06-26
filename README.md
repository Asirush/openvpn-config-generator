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
