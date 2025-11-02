![RPA Suite](https://raw.githubusercontent.com/CamiloCCarvalho/rpa_suite/db6977ef087b1d8c6d1053c6e0bafab6b690ac61/logo-rpa-suite.svg)

<div align="center">

# RPA Suite

**A comprehensive Python toolkit for Robotic Process Automation (RPA) development**

[![PyPI Downloads](https://static.pepy.tech/badge/rpa-suite/month)](https://pepy.tech/projects/rpa_suite)
[![PyPI version](https://img.shields.io/pypi/v/rpa-suite)](https://pypi.org/project/rpa-suite/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rpa-suite)](https://pypi.org/project/rpa-suite/)
[![License MIT](https://img.shields.io/github/license/docling-project/docling)](https://opensource.org/licenses/MIT)

[Documentation](#documentation) • [Installation](#installation) • [Quick Start](#quick-start) • [Features](#features) • [Contributing](#contributing)

</div>

---

## Overview

**RPA Suite** is a powerful and versatile Python library designed to streamline and optimize the development of Robotic Process Automation (RPA) projects. Built with simplicity and efficiency in mind, it provides a comprehensive set of tools that make automation development faster, more reliable, and more maintainable.

Whether you're working with Selenium, Botcity, or building custom automation solutions, RPA Suite offers the essential utilities you need to accelerate your development process.

## Key Features

- **🕐 Time Management** - Schedule executions, wait for specific times, and manage time-based automation flows
- **📧 Email Automation** - Send emails via SMTP with HTML support and attachments
- **📝 Logging System** - Comprehensive logging with file and stream support using Loguru
- **📁 File Operations** - Screenshot capture, file counting, and flag file management
- **🗂️ Directory Management** - Create and manage temporary directories with ease
- **🔍 Text Processing** - Pattern matching, regex operations, and text validation
- **🌐 Browser Automation** - Selenium-based browser control with Chrome support (optional)
- **⚡ Parallel & Async Execution** - Run processes in parallel or asynchronously
- **🤖 Desktop Automation** - PyAutoGUI-based desktop automation (Artemis module)
- **📄 OCR with AI** - Document conversion with OCR capabilities (Iris module - optional)
- **💾 Database Tracking** - Complete execution tracking and management system with multi-database support (SQLite, PostgreSQL, MySQL)
- **🎨 Colored Console Output** - Beautiful terminal output with color-coded messages
- **✅ Data Validation** - Email validation and pattern checking utilities

## Installation

### Basic Installation

Install RPA Suite using pip:

```bash
pip install rpa-suite
```

Or using conda:

```bash
conda install -c conda-forge rpa-suite
```

### Optional Dependencies

For advanced features, install additional dependencies:

```bash
# Browser automation (Selenium)
pip install selenium webdriver-manager

# OCR with AI (Iris module)
pip install docling

# Desktop automation (Artemis - included by default)
# pyautogui is already included
```

## Quick Start

After installation, import and use RPA Suite immediately:

```python
from rpa_suite import rpa

# Send an email
rpa.email.send_smtp(
    email_user="your@email.com",
    email_password="your_password",
    email_to="recipient@email.com",
    subject_title="Hello from RPA Suite",
    body_message="<p>This is a test email</p>"
)

# Schedule a function to run at a specific time
rpa.clock.exec_at_hour('14:30', my_function, arg1, arg2)

# Wait before executing a function
rpa.clock.wait_for_exec(30, my_function)

# Take a screenshot
rpa.file.screen_shot(filename="screenshot.png")

# Print colored messages
rpa.success_print("Operation completed successfully!")
rpa.error_print("An error occurred!")
```

### Database Module Example

Track your automation executions with the Database module:

```python
from rpa_suite import rpa

# Initialize database (SQLite by default)
db = rpa.database()

# Start tracking an execution
exec_id = db.start_execution(automation_name="My Automation Bot")

# Add items to process
item_id = db.add_item(execution_id=exec_id, item_identifier="item_001")

# Finish the execution
db.finish_execution(exec_id, status="completed")
```

## Requirements

### Core Dependencies

- Python 3.11+
- colorama
- colorlog
- email-validator
- loguru
- pillow
- pyautogui
- requests
- opencv-python

### Optional Dependencies

- selenium (for browser automation)
- webdriver-manager (for browser automation)
- docling (for OCR/AI features)
- psycopg2-binary (for PostgreSQL support)
- mysql-connector-python (for MySQL support)

## Features in Detail

### Time Management (Clock Module)

Control execution timing and scheduling:

- `exec_at_hour()` - Execute functions at specific times
- `wait_for_exec()` - Wait before executing functions
- `exec_and_wait()` - Execute and wait pattern

### Email (Email Module)

Send emails with full SMTP support:

- HTML email support
- File attachments
- Custom SMTP configuration
- Email validation

### Logging (Log Module)

Comprehensive logging system based on Loguru:

- File and console logging
- Multiple log levels (debug, info, warning, error, critical)
- Configurable log formats
- Automatic log rotation

### File Operations (File Module)

File and screenshot management:

- Screenshot capture with custom naming
- Flag file creation/deletion for process tracking
- File counting with extension filtering

### Database Tracking (Database Module)

Complete execution lifecycle management:

- Multi-database support (SQLite, PostgreSQL, MySQL)
- Execution tracking with status management
- Item queue processing
- Automatic interruption detection
- Reprocessing capabilities
- Comprehensive statistics and reporting
- Structured logging integration

## Module Structure

### Core Modules

- **clock** - Time management and scheduling
- **date** - Date and time formatting utilities
- **email** - SMTP email sending
- **file** - File operations and screenshots
- **directory** - Directory management
- **log** - Logging system
- **printer** - Colored console output
- **regex** - Pattern matching and regex operations
- **validate** - Data validation utilities

### Advanced Modules

- **database** - Execution tracking and database management
- **browser** - Selenium-based browser automation (optional)
- **parallel** - Parallel process execution
- **async** - Asynchronous execution
- **artemis** - Desktop automation with PyAutoGUI
- **iris** - OCR and document conversion (optional)

### Database Module Methods

**Execution Management:**
- `start_execution()` - Start tracking a new execution
- `finish_execution()` - Complete an execution
- `get_execution()` - Retrieve execution details
- `get_executions()` - List executions with filtering
- `detect_and_mark_interrupted_executions()` - Auto-detect interruptions

**Item Processing:**
- `add_item()` - Add item to processing queue
- `add_items()` - Batch add items
- `get_next_item_from_queue()` - Get next item to process
- `start_processing_item()` - Mark item as processing
- `update_checkpoint()` - Update processing checkpoint
- `finish_item()` - Complete item processing
- `get_item()` - Get item details
- `get_items()` - List items with filtering

**Reprocessing:**
- `can_reprocess_execution()` - Check if execution can be reprocessed
- `reprocess_interrupted_execution()` - Restart interrupted execution
- `can_reprocess_item()` - Check if item can be reprocessed
- `reprocess_interrupted_item()` - Restart interrupted item

**Maintenance:**
- `clear_pending_items()` - Remove pending items
- `clear_interrupted_items()` - Remove interrupted items
- `clear_successful_executions()` - Remove successful executions
- `clear_failed_executions()` - Remove failed executions
- `clear_executions_table()` - Clear all executions
- `clear_items_table()` - Clear all items
- `clear_logs_table()` - Clear all logs
- `clear_database()` - Clear entire database

**Statistics & Logging:**
- `add_log()` - Add log entry
- `get_logs()` - Retrieve execution logs
- `clear_logs()` - Clear execution logs
- `get_statistics()` - Get comprehensive statistics

## Documentation

For detailed documentation, usage examples, and API reference, visit:

- **[GitHub Wiki](https://github.com/CamiloCCarvalho/rpasuite/wiki)** - Complete documentation and guides
- **[PyPI Project Page](https://pypi.org/project/rpa-suite/)** - Package information and releases

## Contributing

Contributions are welcome! If you'd like to contribute to RPA Suite:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Camilo Costa de Carvalho**

- GitHub: [@CamiloCCarvalho](https://github.com/CamiloCCarvalho)
- LinkedIn: [camilocostac](https://www.linkedin.com/in/camilocostac/)
- Email: camilo.costa1993@gmail.com

## Release Notes

### Version 1.6.6

**New Features:**
- ✨ Added Database module for complete execution tracking and lifecycle management
- ✨ Multi-database support (SQLite, PostgreSQL, MySQL)
- ✨ Automatic interruption detection and recovery
- ✨ Item queue processing system
- ✨ Comprehensive statistics and reporting

**Improvements:**
- 🔧 Enhanced Suite instance initialization with proper type hints
- 🔧 Improved autocomplete and IDE support
- 🔧 Better docstrings and module descriptions
- 🔧 Refactored module structure for better maintainability

### Version 1.6.5

- Initial release with core functionality

---

<div align="center">

**[⬆ Back to Top](#rpa-suite)**

Made with ❤️ for the RPA community

</div>
