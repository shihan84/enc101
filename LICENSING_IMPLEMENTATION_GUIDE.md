# Licensing Implementation Guide
## GitHub-Based Monthly Subscription System

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Licensing Models](#licensing-models)
3. [GitHub-Based Licensing Approaches](#github-based-licensing-approaches)
4. [Implementation Architecture](#implementation-architecture)
5. [Payment Integration Options](#payment-integration-options)
6. [Security Considerations](#security-considerations)
7. [Step-by-Step Implementation](#step-by-step-implementation)
8. [Code Structure](#code-structure)
9. [Testing & Validation](#testing--validation)

---

## 🎯 Overview

This guide explains how to implement a **monthly subscription licensing system** for your IBE-100 Enterprise application using GitHub as the license validation server. This approach leverages GitHub's infrastructure for secure, scalable license management.

### Why GitHub for Licensing?

✅ **Free Infrastructure**: GitHub provides free API access and storage  
✅ **Secure**: GitHub's authentication and encryption  
✅ **Scalable**: Handles thousands of license validations  
✅ **Version Control**: Track license changes and revocations  
✅ **Automation**: GitHub Actions for automated license management  
✅ **Private Repositories**: Keep license data secure  

---

## 🔐 Licensing Models

### 1. **Hardware-Based Licensing** (Recommended for Enterprise)
- **License Key**: Tied to machine hardware (CPU ID, MAC address, disk serial)
- **Validation**: Online validation via GitHub API
- **Offline Grace Period**: 7-30 days offline usage
- **Best For**: Desktop applications, single-user licenses

### 2. **User Account Licensing**
- **License Key**: Tied to user account/email
- **Validation**: GitHub API + user authentication
- **Multi-Device**: User can use on multiple machines
- **Best For**: SaaS-style applications, multi-user scenarios

### 3. **Subscription-Based Licensing** (Your Requirement)
- **License Key**: Tied to subscription ID
- **Validation**: Check subscription status via GitHub API
- **Monthly Renewal**: Automatic renewal checks
- **Best For**: Monthly subscription model

### 4. **Feature-Based Licensing**
- **License Key**: Unlocks specific features
- **Tiers**: Basic, Pro, Enterprise tiers
- **Validation**: Feature flags in license data
- **Best For**: Tiered pricing models

---

## 🚀 GitHub-Based Licensing Approaches

### **Approach 1: GitHub Releases + API** (Recommended)

**How It Works:**
1. Create a **private GitHub repository** for license management
2. Store license data in JSON files (one per license key)
3. Use **GitHub Releases** to store encrypted license files
4. Application validates via **GitHub API** (REST or GraphQL)

**Structure:**
```
licenses/
├── licenses.json          # Master license registry
├── active/
│   ├── LICENSE-ABC123.json
│   ├── LICENSE-XYZ789.json
│   └── ...
├── expired/
│   └── ...
└── revoked/
    └── ...
```

**Pros:**
- ✅ Simple to implement
- ✅ Easy to manage licenses
- ✅ Version control for license changes
- ✅ Can use GitHub Actions for automation

**Cons:**
- ⚠️ Requires GitHub API rate limits consideration
- ⚠️ Private repo requires authentication

---

### **Approach 2: GitHub Gists** (Lightweight)

**How It Works:**
1. Store license data in **GitHub Gists** (private)
2. Each license key = one Gist
3. Application validates by fetching Gist content

**Pros:**
- ✅ Very simple
- ✅ Fast API access
- ✅ Easy to update

**Cons:**
- ⚠️ Limited to 300 Gists per user
- ⚠️ Less organized than repository approach

---

### **Approach 3: GitHub Issues + Labels** (For Support Integration)

**How It Works:**
1. Create GitHub Issues for each subscription
2. Use labels: `active`, `expired`, `trial`, `enterprise`
3. Application checks issue status via API

**Pros:**
- ✅ Integrated with support system
- ✅ Can track subscription issues
- ✅ Comments for license notes

**Cons:**
- ⚠️ Slower validation (more API calls)
- ⚠️ Less structured data

---

### **Approach 4: GitHub Database (GitHub + External DB)**

**How It Works:**
1. GitHub repository stores license metadata
2. External database (PostgreSQL/MySQL) stores detailed subscription data
3. Payment processor (Stripe/PayPal) handles billing
4. GitHub Actions syncs data between systems

**Pros:**
- ✅ Most scalable
- ✅ Best for production
- ✅ Handles complex subscription logic

**Cons:**
- ⚠️ Requires external infrastructure
- ⚠️ More complex setup

---

## 🏗️ Implementation Architecture

### **Recommended Architecture: Hybrid Approach**

```
┌─────────────────┐
│   Application   │
│  (Your App)     │
└────────┬────────┘
         │
         │ 1. Validate License
         ▼
┌─────────────────┐
│  License Client │
│  (Python SDK)   │
└────────┬────────┘
         │
         ├──► 2. Check Local Cache
         │    (Offline Grace Period)
         │
         ├──► 3. GitHub API
         │    (Validate License)
         │
         └──► 4. Payment Processor
              (Stripe/PayPal)
              (Check Subscription Status)
```

### **Components:**

1. **License Service** (`src/services/license_service.py`)
   - Validates license keys
   - Checks subscription status
   - Manages offline grace period
   - Handles license caching

2. **GitHub License API** (Private Repository)
   - Stores license data
   - Provides validation endpoint
   - Tracks subscription status

3. **Payment Processor Integration**
   - Stripe (Recommended)
   - PayPal
   - Paddle
   - Gumroad

4. **License Manager UI** (`src/ui/widgets/license_widget.py`)
   - Enter license key
   - View subscription status
   - Renew subscription
   - Manage licenses

---

## 💳 Payment Integration Options

### **Option 1: Stripe** (Recommended)

**Why Stripe?**
- ✅ Most developer-friendly
- ✅ Excellent documentation
- ✅ Webhook support for subscription events
- ✅ Handles recurring billing automatically
- ✅ Supports multiple currencies

**Integration:**
```python
# Stripe handles:
- Subscription creation
- Monthly billing
- Payment processing
- Subscription cancellation
- Webhook events (subscription updated, cancelled, etc.)
```

**Webhook Events:**
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`

---

### **Option 2: PayPal**

**Why PayPal?**
- ✅ Widely accepted
- ✅ Good for international customers
- ✅ Subscription support

**Integration:**
- PayPal Subscriptions API
- Webhook notifications

---

### **Option 3: Paddle**

**Why Paddle?**
- ✅ Handles VAT/taxes automatically
- ✅ Good for SaaS products
- ✅ Built-in license management

---

### **Option 4: Gumroad**

**Why Gumroad?**
- ✅ Simple setup
- ✅ Good for digital products
- ✅ Built-in license keys

---

## 🔒 Security Considerations

### **1. License Key Generation**

**Format:**
```
IBE-100-XXXX-XXXX-XXXX-XXXX
```

**Structure:**
- **Prefix**: `IBE-100` (product identifier)
- **Segments**: 4 groups of 4 characters
- **Algorithm**: Base32 encoding of:
  - Subscription ID
  - Customer ID
  - Expiry date (encrypted)
  - Checksum

**Example:**
```python
def generate_license_key(subscription_id: str, customer_id: str, expiry_date: datetime) -> str:
    """Generate a secure license key"""
    data = f"{subscription_id}:{customer_id}:{expiry_date.isoformat()}"
    encrypted = encrypt(data, secret_key)
    checksum = calculate_checksum(encrypted)
    license_key = f"IBE-100-{format_key(encrypted)}-{checksum}"
    return license_key
```

---

### **2. Hardware Fingerprinting**

**Collect:**
- CPU ID / Processor ID
- MAC Address (primary network adapter)
- Disk Serial Number
- Windows Product ID (if Windows)

**Purpose:**
- Prevent license sharing
- Lock license to specific machine
- Detect license abuse

**Implementation:**
```python
def get_machine_id() -> str:
    """Get unique machine identifier"""
    import platform
    import uuid
    
    # Get MAC address
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                    for elements in range(0,2*6,2)][::-1])
    
    # Get CPU info
    cpu_id = platform.processor()
    
    # Get disk serial (Windows)
    if platform.system() == 'Windows':
        import subprocess
        disk_serial = subprocess.check_output(
            'wmic diskdrive get serialnumber', shell=True
        ).decode().strip()
    else:
        disk_serial = "unknown"
    
    # Combine and hash
    machine_id = f"{mac}:{cpu_id}:{disk_serial}"
    return hashlib.sha256(machine_id.encode()).hexdigest()[:16]
```

---

### **3. License Validation Flow**

```
1. User enters license key
   ↓
2. Validate format (regex)
   ↓
3. Decode license key
   ↓
4. Check local cache (offline grace period)
   ↓
5. If cache expired or invalid:
   ├──► Connect to GitHub API
   ├──► Fetch license data
   ├──► Validate subscription status
   ├──► Check expiry date
   ├──► Verify machine ID (if hardware-locked)
   └──► Update local cache
   ↓
6. If valid:
   ├──► Allow application access
   └──► Start background validation timer
   ↓
7. If invalid:
   ├──► Show error message
   ├──► Offer to renew subscription
   └──► Limit application features (trial mode)
```

---

### **4. Encryption & Obfuscation**

**License Data Encryption:**
- Use **Fernet** (symmetric encryption) - already in your codebase
- Encrypt sensitive data (customer ID, subscription ID)
- Store encryption key securely

**Code Obfuscation:**
- Use PyInstaller with obfuscation
- Consider using **PyArmor** for additional protection
- Obfuscate license validation logic

**API Security:**
- Use **GitHub Personal Access Token** (PAT) with minimal permissions
- Store PAT encrypted in application config
- Rotate PAT periodically
- Use **GitHub App** instead of PAT for production (more secure)

---

## 📝 Step-by-Step Implementation

### **Phase 1: Setup GitHub License Repository**

1. **Create Private Repository:**
   ```
   Repository Name: ibe100-licenses
   Visibility: Private
   Description: License management for IBE-100 Enterprise
   ```

2. **Repository Structure:**
   ```
   ibe100-licenses/
   ├── licenses/
   │   ├── active/
   │   │   └── LICENSE-ABC123.json
   │   ├── expired/
   │   └── revoked/
   ├── .github/
   │   └── workflows/
   │       └── sync-licenses.yml
   ├── LICENSE_SCHEMA.json
   └── README.md
   ```

3. **License File Format:**
   ```json
   {
     "license_key": "IBE-100-XXXX-XXXX-XXXX-XXXX",
     "subscription_id": "sub_1234567890",
     "customer_id": "cus_1234567890",
     "customer_email": "customer@example.com",
     "status": "active",
     "plan": "monthly",
     "created_at": "2024-01-01T00:00:00Z",
     "expires_at": "2024-02-01T00:00:00Z",
     "machine_id": "abc123def456",  // Optional: hardware lock
     "features": {
       "scte35_injection": true,
       "scte35_monitoring": true,
       "epg_generation": true,
       "api_access": true,
       "telegram_notifications": true
     },
     "metadata": {
       "payment_processor": "stripe",
       "last_validated": "2024-01-15T10:30:00Z",
       "validation_count": 42
     }
   }
   ```

---

### **Phase 2: Create License Service**

**File:** `src/services/license_service.py`

**Key Methods:**
- `validate_license(license_key: str) -> LicenseStatus`
- `check_subscription_status(subscription_id: str) -> bool`
- `get_license_info(license_key: str) -> dict`
- `refresh_license_cache() -> bool`
- `is_feature_enabled(feature: str) -> bool`

---

### **Phase 3: Integrate Payment Processor**

**Example: Stripe Integration**

1. **Create Stripe Account**
2. **Set up Webhook Endpoint** (GitHub Actions or separate server)
3. **Handle Webhook Events:**
   - Subscription created → Create license file in GitHub
   - Subscription updated → Update license file
   - Subscription cancelled → Move license to expired folder
   - Payment succeeded → Activate license
   - Payment failed → Send notification

---

### **Phase 4: Add License UI**

**File:** `src/ui/widgets/license_widget.py`

**Features:**
- License key input field
- Subscription status display
- Days remaining counter
- Renew subscription button
- Feature list (enabled/disabled)
- License information panel

---

### **Phase 5: Application Integration**

**Modify:** `main_enterprise.py`

```python
# Add license validation on startup
license_service = LicenseService()
license_status = license_service.validate_license(config.license_key)

if not license_status.is_valid:
    # Show license dialog
    license_dialog = LicenseDialog(license_service)
    if license_dialog.exec() != QDialog.Accepted:
        sys.exit(1)  # Exit if license not validated
```

---

## 💻 Code Structure

### **Directory Structure:**

```
IBE-100_v3.0_ENTERPRISE/
├── src/
│   ├── services/
│   │   ├── license_service.py          # License validation
│   │   └── payment_service.py          # Payment integration
│   ├── models/
│   │   └── license.py                   # License data model
│   ├── ui/
│   │   └── widgets/
│   │       └── license_widget.py       # License UI
│   └── utils/
│       ├── license_validator.py        # License key validation
│       ├── hardware_id.py              # Machine fingerprinting
│       └── encryption.py               # License encryption
├── licenses/                            # Local license cache
│   └── .gitignore                      # Don't commit licenses
└── LICENSE_SCHEMA.json                  # License schema definition
```

---

## 🧪 Testing & Validation

### **Test Scenarios:**

1. **Valid License:**
   - Enter valid license key
   - Application should start normally
   - All features enabled

2. **Expired License:**
   - Enter expired license key
   - Show renewal prompt
   - Limit features (trial mode)

3. **Invalid License:**
   - Enter invalid license key
   - Show error message
   - Offer to purchase

4. **Offline Validation:**
   - Disconnect internet
   - Application should use cached license
   - Show offline mode indicator

5. **License Renewal:**
   - Renew subscription via UI
   - Redirect to payment page
   - Update license after payment

6. **Hardware Lock:**
   - Activate license on Machine A
   - Try to use on Machine B
   - Should show error (if hardware-locked)

---

## 📊 License Status Flow

```
┌─────────────┐
│   Trial     │ (30 days, limited features)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validating │ (Checking license)
└──────┬──────┘
       │
       ├──► Valid ──► ┌─────────────┐
       │               │   Active    │ (Full access)
       │               └─────────────┘
       │
       ├──► Expired ──► ┌─────────────┐
       │                 │   Expired   │ (Renewal required)
       │                 └─────────────┘
       │
       └──► Invalid ──► ┌─────────────┐
                         │   Invalid   │ (Purchase required)
                         └─────────────┘
```

---

## 🔄 Automated License Management

### **GitHub Actions Workflow:**

**File:** `.github/workflows/sync-licenses.yml`

```yaml
name: Sync Licenses

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check Expired Licenses
        run: |
          python scripts/check_expired_licenses.py
      
      - name: Update License Status
        run: |
          python scripts/update_license_status.py
      
      - name: Commit Changes
        run: |
          git config --local user.email "actions@github.com"
          git config --local user.name "GitHub Actions"
          git add .
          git commit -m "Update license statuses" || exit 0
          git push
```

---

## 📈 Monitoring & Analytics

### **Track:**
- License validations per day
- Active subscriptions
- Expired licenses
- Renewal rate
- Feature usage
- License errors

### **Tools:**
- GitHub Insights (repository activity)
- Custom analytics dashboard
- Logging service (Telegram notifications)

---

## 🎯 Next Steps

1. **Choose Licensing Approach** (Recommend: GitHub Releases + API)
2. **Set up Payment Processor** (Recommend: Stripe)
3. **Create License Service** (Python implementation)
4. **Build License UI** (Qt widget)
5. **Integrate with Application** (Startup validation)
6. **Set up GitHub Repository** (Private license repo)
7. **Configure GitHub Actions** (Automated license management)
8. **Test Thoroughly** (All scenarios)
9. **Deploy** (Production rollout)

---

## 📚 Additional Resources

- **Stripe Documentation**: https://stripe.com/docs
- **GitHub API**: https://docs.github.com/en/rest
- **GitHub Actions**: https://docs.github.com/en/actions
- **PyArmor** (Code Obfuscation): https://pyarmor.readthedocs.io

---

## ❓ FAQ

**Q: Can I use GitHub for free?**  
A: Yes, GitHub offers free private repositories for unlimited collaborators.

**Q: What about API rate limits?**  
A: GitHub allows 5,000 requests/hour for authenticated requests. Use caching to minimize API calls.

**Q: Is this secure?**  
A: Yes, with proper encryption, hardware fingerprinting, and secure API tokens.

**Q: Can licenses work offline?**  
A: Yes, implement a grace period (7-30 days) with local license caching.

**Q: How do I handle license revocations?**  
A: Move license file to `revoked/` folder and check this during validation.

---

**Ready to implement?** Let me know which approach you prefer, and I'll help you build it! 🚀

