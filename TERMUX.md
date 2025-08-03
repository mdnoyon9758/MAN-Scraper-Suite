# 📱 MAN Suite - Termux (Android) Guide

## Quick Installation

### Step 1: Install Termux
Download Termux from [F-Droid](https://f-droid.org/packages/com.termux/) (recommended) or Google Play Store.

### Step 2: Update Termux packages
```bash
pkg update && pkg upgrade
```

### Step 3: Clone and Install MAN Suite
```bash
# Install git
pkg install git

# Clone repository
git clone https://github.com/yourusername/MAN-Scraper-Suite.git
cd MAN-Scraper-Suite

# Run Termux installer
python install-termux.py
```

## What Works on Termux

### ✅ **Fully Supported:**
- **Basic Web Scraping** - requests + BeautifulSoup
- **Social Media Scraping** - Reddit, Twitter (no API)
- **PDF Text Extraction** - PyPDF2
- **Image Processing** - Pillow
- **Data Export** - CSV, JSON, Excel
- **Google Sheets Integration** - Full support
- **CLI Interface** - Complete functionality
- **Proxy Support** - HTTP/HTTPS proxies
- **User Agent Spoofing** - fake-useragent

### ⚠️ **Limited Support:**
- **Dynamic JS Scraping** - Not available (no Selenium/Playwright)
- **GUI Interface** - Terminal only
- **Heavy AI Features** - Limited due to resource constraints

### ❌ **Not Supported:**
- **Web Dashboard** - Requires full Flask setup
- **Database Integration** - SQLite only
- **Advanced Automation** - Limited scheduling

## Termux-Specific Usage

### Basic Scraping
```bash
# Simple webpage scraping
python man.py scrape "https://example.com" --format json

# Multiple URLs
python -m manscrapersuite.cli scrape-multiple "https://site1.com" "https://site2.com"
```

### Social Media
```bash
# Reddit scraping (no API required)
python -m manscrapersuite.cli reddit "technology" --limit 20

# Twitter hashtag scraping
python -m manscrapersuite.cli twitter "#python" --count 50
```

### Data Export
```bash
# Export to Google Sheets
python -m manscrapersuite.cli google-auth  # One-time setup
python -m manscrapersuite.cli scrape "https://news.ycombinator.com" --format json
```

## Performance Tips for Android

### 1. **Battery Optimization**
```bash
# Use shorter scraping sessions
python -m manscrapersuite.cli scrape "https://example.com" --format json

# Avoid long-running processes
```

### 2. **Memory Management**
```bash
# Process smaller batches
python -m manscrapersuite.cli scrape-multiple "url1" "url2" --format csv
# Instead of scraping 100+ URLs at once
```

### 3. **Storage**
```bash
# Check available space
df -h

# Clean up regularly
rm -rf scraped_data_*.json
```

## Troubleshooting

### Common Issues:

#### 1. **Installation Fails**
```bash
# Update packages first
pkg update && pkg upgrade

# Install build tools
pkg install clang make pkg-config

# Try again
python install-termux.py
```

#### 2. **SSL Errors**
```bash
# Install certificates
pkg install ca-certificates

# Update pip
pip install --upgrade pip
```

#### 3. **Permission Errors**
```bash
# Grant storage permission in Android settings
# Termux → Permissions → Storage

# Or use internal storage only
cd /data/data/com.termux/files/home
```

#### 4. **Out of Memory**
```bash
# Use lighter requirements
pip install -r requirements-termux.txt

# Clear cache
pip cache purge
```

## Advanced Termux Setup

### 1. **Enable Storage Access**
```bash
termux-setup-storage
# Allows access to Android/data/com.termux/files
```

### 2. **Background Execution**
```bash
# Install Termux:Boot for startup scripts
# Install Termux:Tasker for automation
```

### 3. **Notifications**
```bash
# Install termux-api
pkg install termux-api

# Send notifications
termux-notification --title "Scraping Complete" --content "Data exported"
```

## Example Termux Workflow

```bash
# 1. Start scraping session
cd MAN-Scraper-Suite

# 2. Authenticate (one time)
python -m manscrapersuite.cli google-auth

# 3. Scrape data
python -m manscrapersuite.cli scrape "https://news.ycombinator.com" --format json

# 4. Export to sheets
# (Automatic with authentication)

# 5. Check results
ls -la scraped_*.json
```

## Performance Benchmarks

### Typical Termux Performance:
- **Single webpage**: 2-5 seconds
- **10 webpages**: 30-60 seconds  
- **Reddit posts (50)**: 45-90 seconds
- **Twitter posts (100)**: 60-120 seconds

### Memory Usage:
- **Base CLI**: 20-30MB RAM
- **Active scraping**: 50-100MB RAM
- **Large datasets**: 100-200MB RAM

## Termux vs Desktop Comparison

| Feature | Desktop | Termux | Notes |
|---------|---------|---------|--------|
| Basic Scraping | ✅ | ✅ | Same functionality |
| JS Rendering | ✅ | ❌ | Use mobile-optimized sites |
| Social Media | ✅ | ✅ | No API required methods |
| Export Options | ✅ | ✅ | All formats supported |
| GUI Interface | ✅ | ❌ | Terminal only |
| Performance | 100% | 60-80% | Expected on mobile |

## Tips for Mobile Web Scraping

1. **Target mobile sites** - Often simpler HTML
2. **Use shorter delays** - Mobile connections vary
3. **Batch processing** - Avoid overwhelming device
4. **Regular cleanup** - Limited storage space
5. **Background limits** - Android kills background apps

---

**Happy mobile scraping!** 📱🚀
