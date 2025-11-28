# Telegram-Based Licensing Guide
## How to Use Telegram for Application Licensing

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [How Telegram Licensing Works](#how-telegram-licensing-works)
3. [Setup Instructions](#setup-instructions)
4. [Implementation Architecture](#implementation-architecture)
5. [License Activation Flow](#license-activation-flow)
6. [License Validation Flow](#license-validation-flow)
7. [Telegram Bot Commands](#telegram-bot-commands)
8. [Security Considerations](#security-considerations)
9. [Step-by-Step Implementation](#step-by-step-implementation)

---

## 🎯 Overview

Telegram-based licensing allows you to manage application licenses through a Telegram bot. This approach provides:

✅ **Easy License Management**: Activate, validate, and manage licenses via Telegram  
✅ **Real-Time Notifications**: Get instant alerts about license status  
✅ **User-Friendly**: Customers interact with a simple Telegram bot  
✅ **Secure**: License keys validated through your Telegram bot server  
✅ **Cost-Effective**: No need for external payment processors or servers  
✅ **Remote Control**: Manage licenses from anywhere via Telegram  

---

## 🔄 How Telegram Licensing Works

### **Architecture Overview**

```
┌─────────────────┐
│   Application   │
│  (IBE-210)      │
└────────┬────────┘
         │
         │ 1. Request License Activation
         ▼
┌─────────────────┐
│  Telegram Bot   │
│  (Your Bot)     │
└────────┬────────┘
         │
         ├──► 2. Validate License Key
         ├──► 3. Check Subscription Status
         ├──► 4. Generate Activation Code
         └──► 5. Send Activation Code to User
```

### **Key Components**

1. **Telegram Bot**: Your license management bot (handles activation, validation)
2. **License Database**: Stores license keys, activation codes, expiry dates
3. **Application**: Validates license with Telegram bot on startup
4. **User**: Interacts with bot to activate license

---

## 🚀 Setup Instructions

### **Step 1: Create Your License Management Telegram Bot**

1. **Open Telegram** and search for **@BotFather**
2. Send `/newbot` command
3. Follow instructions to create your bot:
   - Bot name: `IBE-210 License Bot` (or your choice)
   - Bot username: `ibe210_license_bot` (must end with `_bot`)
4. **Copy the Bot Token** (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. **Save the token securely** - you'll need it for your bot server

### **Step 2: Set Up License Database**

You need a database to store licenses. Options:

**Option A: SQLite Database (Simple)**
- Store licenses in a local SQLite file
- Good for small-scale operations
- File: `licenses.db`

**Option B: PostgreSQL/MySQL (Production)**
- Better for multiple users
- Supports concurrent access
- More scalable

**Option C: JSON Files (Development)**
- Simple file-based storage
- Good for testing
- Not recommended for production

### **Step 3: Create License Bot Server**

You'll need a server (Python script) that:
- Listens to Telegram bot messages
- Validates license keys
- Generates activation codes
- Manages license database

**Example Structure:**
```
license_bot/
├── bot_server.py          # Main bot server
├── license_database.py     # Database operations
├── license_validator.py   # License validation logic
├── config.py              # Configuration (bot token, etc.)
└── licenses.db            # SQLite database (if using SQLite)
```

---

## 🏗️ Implementation Architecture

### **License Data Model**

```python
{
    "license_key": "IBE-210-XXXX-XXXX-XXXX-XXXX",
    "activation_code": "ACT-12345678",
    "customer_id": "CUST-001",
    "customer_telegram_id": 123456789,
    "status": "active",  # active, expired, revoked, trial
    "plan": "monthly",   # monthly, yearly, lifetime
    "created_at": "2024-01-01T00:00:00Z",
    "expires_at": "2024-02-01T00:00:00Z",
    "machine_id": "abc123def456",  # Hardware lock (optional)
    "features": {
        "scte35_injection": true,
        "scte35_monitoring": true,
        "epg_generation": true,
        "api_access": true
    },
    "validation_count": 0,
    "last_validated": null
}
```

### **License Key Format**

```
IBE-210-XXXX-XXXX-XXXX-XXXX
```

- **Prefix**: `IBE-210` (product identifier)
- **Segments**: 4 groups of 4 characters (hexadecimal)
- **Total**: 24 characters (including hyphens)

---

## 🔐 License Activation Flow

### **User Activation Process**

```
1. User purchases license (via website, payment processor, etc.)
   ↓
2. User receives license key: IBE-210-XXXX-XXXX-XXXX-XXXX
   ↓
3. User opens Telegram and finds your bot: @ibe210_license_bot
   ↓
4. User sends: /activate IBE-210-XXXX-XXXX-XXXX-XXXX
   ↓
5. Bot validates license key:
   ├──► Valid → Generate activation code
   │   └──► Send activation code to user
   └──► Invalid → Send error message
   ↓
6. User enters activation code in application
   ↓
7. Application validates with bot:
   ├──► Valid → Application activated
   └──► Invalid → Show error, request new code
```

### **Activation Code Format**

```
ACT-XXXXXXXX
```

- **Prefix**: `ACT-`
- **Code**: 8 characters (alphanumeric)
- **Example**: `ACT-1A2B3C4D`

---

## ✅ License Validation Flow

### **Application Startup Validation**

```
1. Application starts
   ↓
2. Check for stored activation code
   ├──► Found → Validate with Telegram bot
   └──► Not found → Show license activation dialog
   ↓
3. Send validation request to Telegram bot:
   POST /validate
   {
     "activation_code": "ACT-1A2B3C4D",
     "machine_id": "abc123def456"
   }
   ↓
4. Bot validates:
   ├──► Valid & Not Expired → Return success
   │   └──► Application starts normally
   ├──► Expired → Return expiry date
   │   └──► Show renewal prompt
   └──► Invalid → Return error
       └──► Show activation dialog
   ↓
5. Cache validation result (offline grace period: 7-30 days)
   ↓
6. Periodic re-validation (every 24 hours)
```

---

## 🤖 Telegram Bot Commands

### **User Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start bot, show welcome message | `/start` |
| `/activate <license_key>` | Activate a license key | `/activate IBE-210-ABCD-1234-EFGH-5678` |
| `/status` | Check license status | `/status` |
| `/renew` | Renew expired license | `/renew` |
| `/help` | Show help message | `/help` |

### **Admin Commands** (For License Management)

| Command | Description | Example |
|---------|-------------|---------|
| `/admin_create <license_key> <plan> <days>` | Create new license | `/admin_create IBE-210-XXXX-XXXX-XXXX-XXXX monthly 30` |
| `/admin_revoke <license_key>` | Revoke a license | `/admin_revoke IBE-210-XXXX-XXXX-XXXX-XXXX` |
| `/admin_extend <license_key> <days>` | Extend license expiry | `/admin_extend IBE-210-XXXX-XXXX-XXXX-XXXX 30` |
| `/admin_list` | List all licenses | `/admin_list` |
| `/admin_stats` | Show license statistics | `/admin_stats` |

---

## 🔒 Security Considerations

### **1. License Key Generation**

```python
import secrets
import hashlib
from datetime import datetime

def generate_license_key(customer_id: str, plan: str) -> str:
    """Generate a secure license key"""
    # Create unique data
    timestamp = datetime.now().isoformat()
    data = f"{customer_id}:{plan}:{timestamp}"
    
    # Generate hash
    hash_obj = hashlib.sha256(data.encode())
    hash_hex = hash_obj.hexdigest()[:16]  # First 16 chars
    
    # Format: IBE-210-XXXX-XXXX-XXXX-XXXX
    segments = [hash_hex[i:i+4] for i in range(0, 16, 4)]
    license_key = f"IBE-210-{'-'.join(segments)}"
    
    return license_key.upper()
```

### **2. Activation Code Generation**

```python
import secrets

def generate_activation_code() -> str:
    """Generate a secure activation code"""
    code = secrets.token_hex(4).upper()  # 8 characters
    return f"ACT-{code}"
```

### **3. Hardware Fingerprinting**

```python
import platform
import uuid
import hashlib

def get_machine_id() -> str:
    """Get unique machine identifier"""
    # Get MAC address
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                    for i in range(0, 8*6, 8)][::-1])
    
    # Get CPU info
    cpu_id = platform.processor()
    
    # Get disk serial (Windows)
    if platform.system() == 'Windows':
        import subprocess
        try:
            disk_serial = subprocess.check_output(
                'wmic diskdrive get serialnumber', shell=True
            ).decode().strip().split('\n')[1].strip()
        except:
            disk_serial = "unknown"
    else:
        disk_serial = "unknown"
    
    # Combine and hash
    machine_id = f"{mac}:{cpu_id}:{disk_serial}"
    return hashlib.sha256(machine_id.encode()).hexdigest()[:16]
```

### **4. API Security**

- **Use HTTPS**: Always use secure connections
- **Rate Limiting**: Limit validation requests per license
- **Token Authentication**: Use secure tokens for bot API
- **Encryption**: Encrypt sensitive data in database

---

## 📝 Step-by-Step Implementation

### **Phase 1: Create License Bot Server**

**File:** `license_bot/bot_server.py`

```python
import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta
import secrets
import hashlib

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_USER_IDS = [123456789]  # Your Telegram user ID

bot = telebot.TeleBot(BOT_TOKEN)

# Database setup
def init_database():
    conn = sqlite3.connect('licenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            license_key TEXT PRIMARY KEY,
            activation_code TEXT UNIQUE,
            customer_id TEXT,
            customer_telegram_id INTEGER,
            status TEXT,
            plan TEXT,
            created_at TEXT,
            expires_at TEXT,
            machine_id TEXT,
            validation_count INTEGER DEFAULT 0,
            last_validated TEXT
        )
    ''')
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
        "Welcome to IBE-210 License Bot!\n\n"
        "Commands:\n"
        "/activate <license_key> - Activate your license\n"
        "/status - Check your license status\n"
        "/help - Show help"
    )

@bot.message_handler(commands=['activate'])
def activate_license(message):
    try:
        # Extract license key from command
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /activate <license_key>")
            return
        
        license_key = parts[1].strip().upper()
        
        # Validate license key format
        if not license_key.startswith('IBE-210-') or len(license_key) != 24:
            bot.reply_to(message, "Invalid license key format!")
            return
        
        # Check if license exists in database
        conn = sqlite3.connect('licenses.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM licenses WHERE license_key = ?', (license_key,))
        license_data = cursor.fetchone()
        
        if not license_data:
            bot.reply_to(message, "License key not found!")
            conn.close()
            return
        
        # Check if already activated
        if license_data[2]:  # activation_code exists
            bot.reply_to(message, 
                f"License already activated!\n"
                f"Activation Code: {license_data[2]}"
            )
            conn.close()
            return
        
        # Generate activation code
        activation_code = f"ACT-{secrets.token_hex(4).upper()}"
        
        # Update database
        cursor.execute('''
            UPDATE licenses 
            SET activation_code = ?, 
                customer_telegram_id = ?,
                status = 'active'
            WHERE license_key = ?
        ''', (activation_code, message.from_user.id, license_key))
        conn.commit()
        conn.close()
        
        bot.reply_to(message,
            f"License activated successfully!\n\n"
            f"Activation Code: {activation_code}\n\n"
            f"Enter this code in the application to activate."
        )
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['status'])
def check_status(message):
    try:
        conn = sqlite3.connect('licenses.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT license_key, status, expires_at, activation_code
            FROM licenses 
            WHERE customer_telegram_id = ?
        ''', (message.from_user.id,))
        license_data = cursor.fetchone()
        conn.close()
        
        if not license_data:
            bot.reply_to(message, "No license found for your account.")
            return
        
        license_key, status, expires_at, activation_code = license_data
        
        status_msg = (
            f"License Status:\n\n"
            f"License Key: {license_key}\n"
            f"Status: {status}\n"
            f"Expires: {expires_at}\n"
            f"Activation Code: {activation_code}"
        )
        
        bot.reply_to(message, status_msg)
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "IBE-210 License Bot Commands:\n\n"
        "/start - Start the bot\n"
        "/activate <license_key> - Activate your license\n"
        "/status - Check your license status\n"
        "/help - Show this help message"
    )
    bot.reply_to(message, help_text)

# Admin commands
@bot.message_handler(commands=['admin_create'])
def admin_create_license(message):
    if message.from_user.id not in ADMIN_USER_IDS:
        bot.reply_to(message, "Access denied!")
        return
    
    try:
        parts = message.text.split(' ', 3)
        if len(parts) < 4:
            bot.reply_to(message, "Usage: /admin_create <license_key> <plan> <days>")
            return
        
        license_key = parts[1].strip().upper()
        plan = parts[2].strip()
        days = int(parts[3].strip())
        
        expires_at = (datetime.now() + timedelta(days=days)).isoformat()
        created_at = datetime.now().isoformat()
        
        conn = sqlite3.connect('licenses.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO licenses 
            (license_key, status, plan, created_at, expires_at)
            VALUES (?, 'pending', ?, ?, ?)
        ''', (license_key, plan, created_at, expires_at))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, f"License created: {license_key}")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

if __name__ == '__main__':
    init_database()
    print("License bot server started!")
    bot.polling()
```

### **Phase 2: Create License Service in Application**

**File:** `src/services/telegram_license_service.py`

```python
import requests
import json
from datetime import datetime
from typing import Optional, Dict
from ..core.logger import get_logger

class TelegramLicenseService:
    """License service using Telegram bot for validation"""
    
    def __init__(self, bot_token: str, bot_username: str):
        self.logger = get_logger("TelegramLicense")
        self.bot_token = bot_token
        self.bot_username = bot_username
        self.api_base = f"https://api.telegram.org/bot{bot_token}"
        
    def validate_activation_code(self, activation_code: str, machine_id: str) -> Dict:
        """
        Validate activation code with Telegram bot
        
        Returns:
            {
                "valid": bool,
                "status": str,
                "expires_at": str,
                "features": dict
            }
        """
        try:
            # In a real implementation, you would:
            # 1. Send a message to your bot with activation code
            # 2. Bot validates and responds
            # 3. Parse response
            
            # For now, this is a placeholder
            # You'll need to implement the actual validation logic
            
            return {
                "valid": False,
                "status": "not_implemented",
                "message": "Telegram license validation not yet implemented"
            }
            
        except Exception as e:
            self.logger.error(f"License validation error: {e}")
            return {
                "valid": False,
                "status": "error",
                "message": str(e)
            }
    
    def activate_license(self, license_key: str) -> Dict:
        """Activate license via Telegram bot"""
        # Implementation: Send /activate command to bot
        pass
```

### **Phase 3: Add License UI Widget**

**File:** `src/ui/widgets/license_widget.py`

```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt

class LicenseWidget(QWidget):
    """Widget for license activation and management"""
    
    def __init__(self, license_service):
        super().__init__()
        self.license_service = license_service
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # License Key Input
        key_group = QGroupBox("License Activation")
        key_layout = QVBoxLayout()
        
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("Enter license key: IBE-210-XXXX-XXXX-XXXX-XXXX")
        key_layout.addWidget(QLabel("License Key:"))
        key_layout.addWidget(self.license_key_input)
        
        self.activate_btn = QPushButton("Activate via Telegram")
        self.activate_btn.clicked.connect(self._activate_license)
        key_layout.addWidget(self.activate_btn)
        
        key_group.setLayout(key_layout)
        layout.addWidget(key_group)
        
        # Activation Code Input
        code_group = QGroupBox("Enter Activation Code")
        code_layout = QVBoxLayout()
        
        self.activation_code_input = QLineEdit()
        self.activation_code_input.setPlaceholderText("Enter activation code: ACT-XXXXXXXX")
        code_layout.addWidget(QLabel("Activation Code:"))
        code_layout.addWidget(self.activation_code_input)
        
        self.validate_btn = QPushButton("Validate & Activate")
        self.validate_btn.clicked.connect(self._validate_activation)
        code_layout.addWidget(self.validate_btn)
        
        code_group.setLayout(code_layout)
        layout.addWidget(code_group)
        
        # Status Display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        layout.addWidget(self.status_display)
    
    def _activate_license(self):
        license_key = self.license_key_input.text().strip()
        if not license_key:
            self.status_display.append("Please enter a license key!")
            return
        
        # Show instructions to user
        self.status_display.append(
            f"To activate your license:\n"
            f"1. Open Telegram\n"
            f"2. Find bot: @{self.license_service.bot_username}\n"
            f"3. Send: /activate {license_key}\n"
            f"4. Copy the activation code you receive\n"
            f"5. Enter it below and click 'Validate & Activate'"
        )
    
    def _validate_activation(self):
        activation_code = self.activation_code_input.text().strip()
        if not activation_code:
            self.status_display.append("Please enter an activation code!")
            return
        
        # Validate with license service
        result = self.license_service.validate_activation_code(activation_code)
        
        if result.get("valid"):
            self.status_display.append("License activated successfully!")
        else:
            self.status_display.append(f"Activation failed: {result.get('message')}")
```

---

## 📊 License Management Workflow

### **For License Administrators**

1. **Create License Key**
   - Generate license key: `IBE-210-XXXX-XXXX-XXXX-XXXX`
   - Add to database with expiry date
   - Send to customer via email/Telegram

2. **Customer Activates**
   - Customer uses `/activate` command in Telegram
   - Bot generates activation code
   - Customer enters code in application

3. **Monitor Licenses**
   - Use `/admin_list` to see all licenses
   - Use `/admin_stats` for statistics
   - Revoke licenses with `/admin_revoke`

4. **Handle Renewals**
   - Use `/admin_extend` to extend expiry
   - Or create new license key

---

## 🎯 Next Steps

1. **Set up Telegram Bot**: Create bot with @BotFather
2. **Create Bot Server**: Implement license bot server (Python)
3. **Set up Database**: Create license database (SQLite/PostgreSQL)
4. **Implement License Service**: Add to application
5. **Create License UI**: Add activation widget
6. **Test Activation Flow**: Test end-to-end
7. **Deploy Bot Server**: Host bot server (VPS, cloud, etc.)
8. **Production Rollout**: Deploy to customers

---

## 📚 Additional Resources

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **python-telegram-bot**: https://python-telegram-bot.org/
- **Telegram Bot Examples**: https://github.com/python-telegram-bot/python-telegram-bot/tree/master/examples

---

## ❓ FAQ

**Q: Do I need a server to run the bot?**  
A: Yes, you need a server (VPS, cloud instance, or even a Raspberry Pi) to run the bot 24/7.

**Q: Can I use a free hosting service?**  
A: Yes, services like Heroku, Railway, or Render offer free tiers for bot hosting.

**Q: How secure is this approach?**  
A: Very secure if implemented correctly with encryption, rate limiting, and proper validation.

**Q: Can licenses work offline?**  
A: Yes, implement a grace period (7-30 days) with local license caching.

**Q: How do I handle license revocations?**  
A: Update license status in database, bot will reject validation on next check.

---

**Ready to implement?** Let me know if you need help setting up the bot server or integrating it into the application! 🚀

