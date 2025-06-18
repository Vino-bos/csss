# Telegram File Converter Bot

## Overview

This is a Python-based Telegram bot designed for file conversion and management operations. The bot provides comprehensive functionality for converting between different file formats (TXT, VCF, XLSX), managing contacts, and performing various file operations. It features user access control, database integration for logging, and automated deployment capabilities.

## System Architecture

### Core Architecture
- **Framework**: Python 3.11 with python-telegram-bot library
- **Database**: SQLite3 for user management and operation logging
- **File Storage**: Temporary file system storage in `/temp` directory
- **Deployment**: Configured for both Replit and Heroku platforms
- **Authentication**: User-based access control with owner privileges

### Technology Stack
- **Backend**: Python 3.11
- **Bot Framework**: python-telegram-bot (v22.1+)
- **Data Processing**: pandas, openpyxl for Excel operations
- **Contact Management**: vobject for VCF file handling
- **Database**: SQLite3 (built-in Python)
- **Deployment**: Heroku, Replit, GitHub Actions CI/CD

## Key Components

### 1. Bot Handlers (`bot/handlers.py`)
- **Purpose**: Main command handlers and user interaction logic
- **Architecture Decision**: Centralized handler system for maintainability
- **Key Features**: Command routing, user authentication checks, inline keyboards

### 2. File Converters (`bot/file_converters.py`)
- **Purpose**: Handle file format conversions (TXT↔VCF, XLSX→VCF)
- **Architecture Decision**: Modular converter functions for extensibility
- **Supported Formats**: TXT, VCF (vCard), XLSX (Excel)

### 3. File Managers (`bot/file_managers.py`)
- **Purpose**: File manipulation operations (rename, merge, split)
- **Architecture Decision**: Separate module for file operations to maintain clean separation of concerns

### 4. Contact Utils (`bot/contact_utils.py`)
- **Purpose**: VCF contact manipulation and analysis
- **Architecture Decision**: Specialized module for contact operations using vobject library

### 5. User Management (`bot/user_manager.py`)
- **Purpose**: Access control and user authorization
- **Architecture Decision**: Database-backed user management with owner privileges
- **Security Model**: Whitelist-based access control

### 6. Database Layer (`bot/database.py`)
- **Purpose**: SQLite database operations and schema management
- **Architecture Decision**: SQLite chosen for simplicity and zero-configuration deployment
- **Tables**: authorized_users, bug_reports, file_operations

### 7. Utilities (`utils/helpers.py`)
- **Purpose**: Common helper functions for file operations
- **Architecture Decision**: Centralized utilities to reduce code duplication

## Data Flow

### 1. User Authentication Flow
```
User Command → check_user_access() → Database Query → Allow/Deny Access
```

### 2. File Conversion Flow
```
File Upload → Temporary Storage → Processing → Output Generation → File Delivery → Cleanup
```

### 3. Command Processing Flow
```
Telegram Update → Handler Router → Access Check → Command Execution → Response
```

## External Dependencies

### Core Dependencies
- **python-telegram-bot**: Telegram Bot API wrapper
- **pandas**: Data manipulation for Excel/CSV processing
- **openpyxl**: Excel file reading/writing
- **vobject**: VCF (vCard) file parsing and generation

### System Dependencies
- **SQLite3**: Built-in Python database
- **File System**: Local temporary storage

## Deployment Strategy

### Multi-Platform Support
- **Primary**: Replit deployment with Nix package management
- **Secondary**: Heroku deployment with Procfile configuration
- **CI/CD**: GitHub Actions for automated testing and deployment

### Environment Configuration
- **Bot Token**: Environment variable `BOT_TOKEN`
- **Python Version**: 3.11 (Replit) / 3.9 (Heroku fallback)
- **Auto-scaling**: Configured for both web and worker processes

### Deployment Commands
```bash
# Replit
pip install python-telegram-bot pandas openpyxl vobject && mkdir -p temp && python main.py

# Heroku
python main.py
```

## Changelog
- June 18, 2025: Initial setup and architecture
- June 18, 2025: Bot successfully deployed and running with token 8131425355:AAFWisLEDBnXm-NsJq-6EgVh247n4o7NwOY
- June 18, 2025: Fixed async/await issues and bot startup errors
- June 18, 2025: Owner ID configured to 7614202330
- June 18, 2025: Added comprehensive README.md with deployment instructions

## Recent Changes

✓ Bot is now successfully running and connected to Telegram API
✓ All file conversion and management features are operational
✓ Database initialization completed
✓ GitHub Actions workflow configured for continuous deployment
✓ README.md created with complete setup instructions
✓ Bot token hardcoded for reliable operation

## User Preferences

Preferred communication style: Simple, everyday language (Bahasa Indonesia).
Bot Owner: User ID 7614202330
Token: 8131425355:AAFWisLEDBnXm-NsJq-6EgVh247n4o7NwOY (configured and working)

## Additional Notes

### Architecture Decisions Rationale

1. **SQLite Database Choice**: 
   - **Problem**: Need persistent storage for user management
   - **Solution**: SQLite for zero-configuration deployment
   - **Pros**: No external database required, built-in Python support
   - **Cons**: Limited to single-process applications

2. **Modular Handler Architecture**:
   - **Problem**: Managing multiple bot commands and features
   - **Solution**: Separate modules for different functionalities
   - **Pros**: Maintainable, extensible, clear separation of concerns
   - **Cons**: Slightly more complex file structure

3. **Temporary File Management**:
   - **Problem**: File processing requires temporary storage
   - **Solution**: `/temp` directory with automatic cleanup
   - **Pros**: Prevents disk space issues, secure file handling
   - **Cons**: Files don't persist between sessions

4. **Access Control System**:
   - **Problem**: Bot needs user management for security
   - **Solution**: Database-backed whitelist with owner privileges
   - **Pros**: Secure, manageable user base
   - **Cons**: Requires manual user addition by owner

The bot is designed for scalability and maintainability, with clear separation between different functional areas and robust error handling throughout the system.