# 🚀 Broadcast Encoder 110 - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying Broadcast Encoder 110 to production environments.

---

## Pre-Deployment Checklist

### ✅ **Requirements Verification**

- [ ] TSDuck installed and accessible
- [ ] System meets minimum requirements
- [ ] Sufficient disk space (2GB+ recommended)
- [ ] Network connectivity verified
- [ ] Firewall rules configured (if needed)
- [ ] Backup strategy defined

### ✅ **Application Preparation**

- [ ] Application executable available
- [ ] Configuration files prepared
- [ ] Profiles configured (if needed)
- [ ] Telegram bot configured (if using notifications)
- [ ] API settings configured (if using API)

---

## Deployment Steps

### Step 1: Backup Existing Installation

If upgrading from a previous version:

```powershell
.\scripts\backup.ps1 -BackupType full
```

This creates a full backup of:
- Database
- Configuration
- Profiles
- SCTE-35 markers

### Step 2: Stop Application

```powershell
.\scripts\deploy.ps1 -Action stop
```

Or manually:
- Close application if running
- Kill any TSDuck processes if needed

### Step 3: Deploy Application

**Option A: Automated Deployment**
```powershell
.\scripts\deploy.ps1 -Action deploy
```

**Option B: Manual Deployment**
1. Extract application to deployment directory
2. Verify executable exists: `dist\IBE-100_Enterprise.exe`
3. Verify required directories will be created on first run

### Step 4: Verify Deployment

```powershell
.\scripts\deploy.ps1 -Action verify
```

This checks:
- Required directories exist
- TSDuck is accessible
- Configuration is valid

### Step 5: Start Application

```powershell
.\scripts\deploy.ps1 -Action start
```

Or manually:
- Run `IBE-100_Enterprise.exe`
- Verify application starts without errors
- Check logs for any issues

---

## Post-Deployment

### Verification

1. **Check Application Status:**
   - Application window opens
   - No error messages
   - All tabs load correctly

2. **Test Health Endpoint** (if API enabled):
   ```bash
   curl http://localhost:8080/api/health
   ```

3. **Test Stream Processing:**
   - Configure a test stream
   - Start processing
   - Verify monitoring works

4. **Check Logs:**
   - Review `logs/app.log` for errors
   - Check `logs/errors.log` for warnings

### Monitoring Setup

1. **Configure Monitoring:**
   - Set up Telegram notifications (optional)
   - Configure monitoring thresholds
   - Enable quality monitoring

2. **Set Up Prometheus** (if using):
   - Configure Prometheus to scrape `/metrics` endpoint
   - Set up Grafana dashboards (optional)

3. **Set Up Automated Backups:**
   - Schedule backup script (Windows Task Scheduler)
   - Configure backup retention policy

---

## Automated Backups

### Setup Automated Backups

**Windows Task Scheduler:**

1. Open Task Scheduler
2. Create Basic Task
3. Configure:
   - **Trigger:** Daily at 2:00 AM
   - **Action:** Start a program
   - **Program:** `powershell.exe`
   - **Arguments:** `-File "E:\path\to\scripts\backup.ps1" -BackupType full`

### Backup Types

**Full Backup:**
```powershell
.\scripts\backup.ps1 -BackupType full
```

**Database Only:**
```powershell
.\scripts\backup.ps1 -BackupType database
```

**Configuration Only:**
```powershell
.\scripts\backup.ps1 -BackupType config
```

**Profiles Only:**
```powershell
.\scripts\backup.ps1 -BackupType profiles
```

### Backup Retention

- Default: Keeps last 10 backups
- Configure with `-MaxBackups` parameter
- Old backups automatically cleaned up

---

## Rollback Procedure

### If Deployment Fails

1. **Stop Application:**
   ```powershell
   .\scripts\deploy.ps1 -Action stop
   ```

2. **Restore from Backup:**
   - Locate backup in `backups/` directory
   - Restore files:
     - `database/sessions.db` from `backups/database_*.db`
     - `config/` from `backups/config_*/`
     - `profiles/` from `backups/profiles_*/`

3. **Restart Application:**
   ```powershell
   .\scripts\deploy.ps1 -Action start
   ```

### Manual Rollback

1. Stop application
2. Restore files from backup directory
3. Restart application
4. Verify functionality

---

## Production Configuration

### Recommended Settings

**API Configuration:**
```json
{
  "api_enabled": false,  // Disable if not needed
  "api_host": "127.0.0.1",  // Localhost only
  "api_port": 8080
}
```

**Logging:**
```json
{
  "log_level": "INFO",  // Use INFO for production
  "log_dir": "logs"
}
```

**Telegram:**
- Enable for production monitoring
- Configure bot token and chat ID
- Test notifications

### Security Hardening

1. **Disable API** if not needed
2. **Configure Firewall:**
   - Block unnecessary ports
   - Allow only required connections
3. **Secure Logs:**
   - Restrict log directory access
   - Rotate logs regularly
4. **Use HTTPS** (via reverse proxy) if API is exposed

---

## Monitoring

### Health Checks

**Simple Health Check:**
```bash
curl http://localhost:8080/health
```

**Comprehensive Health Check:**
```bash
curl http://localhost:8080/api/health
```

### Prometheus Metrics

**Metrics Endpoint:**
```bash
curl http://localhost:8080/metrics
```

**Metrics Include:**
- System CPU usage
- System memory usage
- System disk usage
- Stream status
- Stream packets processed
- Stream errors
- SCTE-35 markers injected

### Log Monitoring

**Key Log Files:**
- `logs/app.log` - Application logs
- `logs/errors.log` - Error logs
- `logs/crashes/` - Crash reports
- `logs/audit.log` - Audit trail

**Monitor For:**
- Error patterns
- Performance degradation
- Resource exhaustion
- Security events

---

## Troubleshooting

### Deployment Issues

**Application Won't Start:**
1. Check TSDuck installation
2. Review crash logs
3. Verify system requirements
4. Check file permissions

**Configuration Errors:**
1. Review `config/app_config.json`
2. Check encryption key exists
3. Verify configuration format

**Backup Failures:**
1. Check disk space
2. Verify directory permissions
3. Review backup script logs

### Performance Issues

**High CPU Usage:**
- Reduce monitoring frequency
- Close unnecessary tabs
- Check for TSDuck process issues

**High Memory Usage:**
- Review log file sizes
- Clean old logs
- Restart application periodically

**Network Issues:**
- Verify input stream accessibility
- Check output destination
- Review firewall rules

---

## Maintenance

### Regular Maintenance Tasks

**Daily:**
- Review error logs
- Check application health
- Monitor stream status

**Weekly:**
- Review audit logs
- Check disk space
- Verify backups

**Monthly:**
- Review performance metrics
- Update dependencies (if needed)
- Security audit

### Update Procedure

1. **Backup:**
   ```powershell
   .\scripts\backup.ps1 -BackupType full
   ```

2. **Stop Application:**
   ```powershell
   .\scripts\deploy.ps1 -Action stop
   ```

3. **Deploy Update:**
   - Replace executable
   - Update configuration if needed

4. **Verify:**
   ```powershell
   .\scripts\deploy.ps1 -Action verify
   ```

5. **Start:**
   ```powershell
   .\scripts\deploy.ps1 -Action start
   ```

---

## Disaster Recovery

### Backup Restoration

1. **Identify Backup:**
   - List backups: Check `backups/` directory
   - Select appropriate backup

2. **Stop Application:**
   ```powershell
   .\scripts\deploy.ps1 -Action stop
   ```

3. **Restore Files:**
   - Database: Copy from `backups/database_*.db`
   - Config: Copy from `backups/config_*/`
   - Profiles: Copy from `backups/profiles_*/`

4. **Restart Application:**
   ```powershell
   .\scripts\deploy.ps1 -Action start
   ```

### Data Recovery

**Database Recovery:**
- Restore from `backups/database_*.db`
- Verify database integrity
- Check session history

**Configuration Recovery:**
- Restore from `backups/config_*/`
- Verify encryption key exists
- Test configuration loading

---

## Support

### Getting Help

1. **Check Logs:**
   - Application logs
   - Error logs
   - Crash logs

2. **Review Documentation:**
   - User Manual
   - Installation Guide
   - Troubleshooting sections

3. **Contact Support:**
   - Provide error messages
   - Include relevant log files
   - Describe deployment steps taken

---

**Version:** 3.0.0 Enterprise  
**Last Updated:** 2024-01-XX

