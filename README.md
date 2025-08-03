# 🔥 MAN Suite - Web Scraping Toolkit

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Cross Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android-blue)](https://github.com/)

🎁 **100% FREE - CROSS-PLATFORM - ALL FEATURES UNLOCKED**

MAN Scraper Suite is a 100% free web scraping and automation toolkit that provides all premium features without limits. Designed for ethical data extraction, it supports scraping across websites, social media platforms, and public APIs without any paywalls or subscriptions.

## ✨ Features

### 🔥 Core Scraping
- **Universal Scraping Engine**: Works with any website, including static and dynamic JS sites
- **Social Media Integration**: Scrape X/Twitter, Reddit, and Instagram (Public profiles only)
- **PDF/Image Scraping**: Extract text and metadata from PDFs, bulk image downloading
- **Real-time Scraping**: Live data collection from multiple sources simultaneously

### 🤖 AI-Powered Intelligence
- **AI Analysis**: Google Gemini API integration for intelligent data insights
- **Smart Filtering**: AI-powered data filtering and prioritization
- **Sentiment Analysis**: Automatic sentiment detection and analysis
- **Content Summarization**: AI-generated summaries of scraped data

### 📊 Advanced Analytics
- **User Behavior Analytics**: Comprehensive user activity tracking and insights
- **Interactive Dashboards**: Real-time analytics with interactive visualizations
- **Anomaly Detection**: Automatic detection of suspicious patterns
- **Export Analytics**: Professional analytics reports in multiple formats

### 📄 Professional Export Options
- **Multiple Formats**: CSV, JSON, Excel, and PDF with professional styling
- **Cloud Integration**: Google Drive, Dropbox, and Google Sheets
- **Database Support**: MySQL, PostgreSQL, MongoDB direct integration
- **Structured Data**: Metadata-rich exports with timestamps and source tracking

### 🔒 Privacy & Compliance
- **GDPR Compliance**: Built-in privacy protection and data anonymization
- **Enhanced Stealth**: Dynamic rate limiting, proxy rotation, user-agent spoofing
- **Ethical Scraping**: Respects robots.txt and implements ethical guidelines
- **Audit Logging**: Complete compliance and audit trail system

### 🌐 User Experience
- **Enhanced CLI**: Interactive command-line with AI commands (Primary Interface)
- **Web Dashboard**: Under development (temporarily disabled)
- **User Management**: Multi-tier user system with activity tracking
- **Mobile Support**: Compatible with Termux/Android

### 🔄 Automation & Integration
- **Smart Scheduling**: Advanced task scheduling and automation
- **Notification System**: Email, Telegram, and webhook notifications
- **API Integration**: RESTful API for third-party integrations
- **Zapier/IFTTT**: Connect with hundreds of external services

## Who's This For?

- **Journalists**: Great for investigating public data.
- **Researchers**: Useful for compiling academic datasets.
- **Activists**: Helps in archiving censored content.
- **Small Businesses**: Provides an edge in competitor price tracking.

## Technical Blueprint

- **Language**: Python 3.10+
- **Core Libraries**: Scrapy, Playwright, Pandas, PyPDF2
- **License**: GPLv3

## Quick Start

### 🖥️ **Desktop Installation (Windows/Linux/macOS)**:

Clone the repository and navigate to the directory:
```bash
$ git clone https://github.com/mdnoyon9758/MAN-Scraper-Suite.git
$ cd MAN-Scraper-Suite
```

Install required dependencies:
```bash
$ pip install -r requirements.txt
# OR use the installer
$ python install.py
```

### 📱 **Android/Termux Installation**:

For Android users with Termux:
```bash
$ pkg install git python
$ git clone https://github.com/mdnoyon9758/MAN-Scraper-Suite.git
$ cd MAN-Scraper-Suite
$ python install-termux.py
```

📖 **See [TERMUX.md](TERMUX.md) for detailed Android setup guide**

2. **Usage**:

**Basic Web Scraping:**
```bash
# Scrape a single webpage
$ python -m manscrapersuite.cli scrape "https://example.com" --format pdf

# Scrape multiple URLs
$ python -m manscrapersuite.cli scrape-multiple "https://site1.com" "https://site2.com" --format csv

# Dynamic JavaScript scraping
$ python -m manscrapersuite.cli scrape "https://spa-site.com" --dynamic --format excel
```

**AI-Powered Features:**
```bash
# Analyze scraped data with AI
$ python -m manscrapersuite.cli analyze data.json --topic "market trends"

# Smart data filtering
$ python -m manscrapersuite.cli smart-filter data.json --criteria "technology news" --output filtered
```

**Social Media Scraping:**
```bash
# Scrape Reddit posts
$ python -m manscrapersuite.cli reddit "technology" --limit 50

# Scrape Twitter hashtags
$ python -m manscrapersuite.cli twitter "#AI" --count 100
```

**Web Dashboard (Temporarily Disabled):**
```bash
# Web dashboard is under development
# All functionality available through CLI commands
$ python -m manscrapersuite.cli --help
```

**Advanced Features:**
```bash
# Test proxy connections
$ python -m manscrapersuite.cli proxy-test

# Show configuration
$ python -m manscrapersuite.cli config-show

# Check version and features
$ python -m manscrapersuite.cli version
```

4. **Configuration**:

Modify `config/default_config.yaml` to adjust default settings.

## Contribution Guidelines

MAN Scraper Suite is community-driven. Contributions to improve the tool are welcome. Please follow the contribution guidelines in `CONTRIBUTING.md`. 

## License

This project is licensed under the terms of the GNU General Public License v3 (GPLv3).

## Support

For any questions, suggestions, or issues, please open an issue in the GitHub repository.
