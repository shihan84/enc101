# Broadcast Encoder 110 - Enterprise Edition

## Overview

Broadcast Encoder 110 is an enterprise-grade broadcast streaming application with comprehensive SCTE-35 support, real-time monitoring, EPG/EIT generation, and Telegram notifications.

## Features

### ✅ Core Features
- **Multi-Protocol Support**: HLS, SRT, UDP, TCP, HTTP/HTTPS, DVB, ASI
- **SCTE-35 Integration**: Full support for ad insertion markers (CUE-OUT, CUE-IN, PREROLL, CUE-CRASH)
- **Profile Management**: Save and load stream configurations per profile
- **Real-Time Monitoring**: System metrics, stream status, SCTE-35 events
- **EPG/EIT Generation**: Electronic Program Guide with full metadata support
- **Telegram Notifications**: Real-time alerts for SCTE-35 events, errors, and status

### ✅ Enterprise Features
- **Profile-Specific Configuration**: Each profile has its own Telegram settings and SCTE-35 directory
- **Encrypted Configuration**: Sensitive data encrypted at rest
- **REST API**: Remote control and automation
- **Health Checks**: Application and service health monitoring
- **Prometheus Metrics**: Export metrics for external monitoring
- **Automated Backups**: Database and configuration backups
- **Input Validation**: Comprehensive validation for all inputs
- **API Rate Limiting**: Protection against API abuse

## Requirements

- Python 3.9+
- TSDuck (installed and in PATH)
- Windows 10/11 (or Linux with Qt6 support)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd FINAL
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the application**:
   ```bash
   python build.py
   ```
   Or manually:
   ```bash
   pyinstaller IBE-100_Enterprise.spec
   ```

## Usage

### Starting the Application

Run the built executable:
```bash
dist\IBE-100_Enterprise.exe
```

Or run from source:
```bash
python main_enterprise.py
```

### Configuration

1. **Create a Profile**: Go to Configuration tab → Create/Select profile
2. **Configure Stream**: Set input/output URLs and parameters
3. **Generate SCTE-35 Markers**: Go to SCTE-35 tab → Generate markers
4. **Start Stream**: Click "▶️ Start" button

### Profile-Specific Settings

Each profile can have:
- Its own Telegram bot token and chat ID
- Its own SCTE-35 marker directory
- Its own stream configuration

## Documentation

- `USER_MANUAL.md` - Complete user guide
- `INSTALLATION_GUIDE.md` - Installation instructions
- `DEPLOYMENT_GUIDE.md` - Deployment procedures
- `PROFILE_SPECIFIC_CONFIGURATION.md` - Profile-specific settings guide
- `PRODUCTION_READINESS_ASSESSMENT.md` - Production readiness details

## Development

### Project Structure

```
FINAL/
├── src/
│   ├── core/           # Core application framework
│   ├── models/          # Data models
│   ├── services/        # Business logic services
│   ├── ui/              # PyQt6 user interface
│   ├── api/             # REST API
│   ├── database/        # Database layer
│   └── utils/           # Utility functions
├── tests/               # Unit and integration tests
├── scripts/             # Utility scripts
├── config/              # Configuration files
├── profiles/            # Profile storage
└── main_enterprise.py   # Application entry point
```

### Running Tests

```bash
pytest tests/
```

### Building

```bash
python build.py
```

## License

© 2024 Broadcast Encoder 110

## Support

For issues and questions, please open an issue in the repository.

