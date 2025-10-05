# Privacy Policy - Wedding Planning OCR Pipeline

## Overview

This wedding planning OCR pipeline is designed to help you organize and process your wedding planning documents while maintaining strict privacy and data protection standards.

## Data Collection & Processing

### What Data We Process
- **Wedding planning documents**: Venue information, vendor contacts, pricing details, timelines
- **Image files**: Photos of wedding planning materials (menus, contracts, brochures)
- **OCR text**: Extracted text content from your uploaded images
- **Metadata**: File creation dates, processing timestamps, quality scores

### What We Don't Collect
- ❌ Personal identification beyond what's in your documents
- ❌ Financial account information or payment details
- ❌ Social security numbers or government IDs
- ❌ Unnecessary personal data outside wedding planning scope

## Data Processing Methods

### Local Processing
- **Image preprocessing** happens locally on your machine
- **File organization** and consolidation occurs locally
- **Export generation** (RTF files) is performed locally

### External API Usage
- **OpenAI GPT-4o Vision API**: Used for OCR text extraction and formatting
- **Pinterest Business API** (Phase 2): For gathering additional wedding inspiration data
- All API communications use encrypted HTTPS connections

### Data Retention
- **Local files**: Remain on your machine indefinitely under your control
- **API processing**: OpenAI processes images temporarily for OCR (see OpenAI's data policy)
- **No permanent storage**: We don't store your data on external servers

## Privacy Protection Measures

### Technical Safeguards
- ✅ **Environment variables**: API keys stored securely in `.env` files
- ✅ **Local processing**: Maximum processing done on your local machine
- ✅ **Encrypted transmission**: All API calls use HTTPS/TLS encryption
- ✅ **No telemetry**: No usage analytics or tracking implemented

### Data Minimization
- Only wedding-related content is extracted from images
- Processing focuses on vendor contacts, pricing, and venue information
- Personal details outside wedding planning are ignored or marked as 'TBD'

### User Control
- 🎛️ **Full ownership**: All processed data remains on your local machine
- 🗑️ **Easy deletion**: Clean output directories task removes all processed data
- ⚙️ **Configurable**: You control which images to process and when
- 📤 **Export control**: You decide when and where to export consolidated data

## Third-Party Services

### OpenAI API
- **Purpose**: OCR text extraction and intelligent formatting
- **Data sent**: Image files containing wedding planning documents
- **Data retention**: Per OpenAI's data usage policy (typically 30 days)
- **Privacy policy**: https://openai.com/privacy/

### Pinterest API (Future - Phase 2)
- **Purpose**: Gathering additional wedding inspiration and vendor information
- **Data accessed**: Your Pinterest boards and pins (read-only)
- **Data retention**: Processed locally, not stored externally
- **Privacy policy**: https://policy.pinterest.com/privacy-policy

## Your Rights & Controls

### Data Access
- 📁 **Full access**: All processed data is stored locally in `src/ocr_md/`
- 📊 **Processing logs**: Task outputs show what was processed and when
- 🔍 **Quality metrics**: Processing quality scores help you understand results

### Data Modification
- ✏️ **Edit results**: All markdown files can be manually edited
- 🔄 **Reprocess**: Re-run OCR on any image at any time
- 🎯 **Selective processing**: Process only specific images when needed

### Data Deletion
- 🧹 **Clean slate**: Use "Clean Output Directories" task to remove all processed data
- 🗂️ **Selective removal**: Delete specific processed files manually
- 💾 **Source preservation**: Original images remain untouched unless you delete them

## Security Best Practices

### For Users
- 🔐 **Secure API keys**: Keep your `.env` file private and never commit it to version control
- 🔒 **Local storage**: Process sensitive documents on secure, private computers
- 🛡️ **Regular updates**: Keep dependencies updated for security patches
- 📱 **Device security**: Use secure devices with up-to-date antivirus protection

### Implementation
- 🔑 **Environment isolation**: Virtual environment isolates dependencies
- 🚫 **No hardcoded secrets**: All sensitive configuration in environment variables
- ⚡ **Minimal dependencies**: Limited external packages reduce attack surface
- 🔄 **Error handling**: Graceful failure handling prevents data leakage

## Data Breach Response

In the unlikely event of a security issue:

1. **Immediate action**: Stop processing and secure your local environment
2. **Assessment**: Determine what data might have been affected
3. **API key rotation**: Generate new OpenAI API keys if compromise suspected
4. **Clean environment**: Re-create virtual environment and update dependencies

## Changes to Privacy Policy

- **Version**: 1.0 (October 2025)
- **Updates**: Any changes will be documented in this file with version history
- **Notification**: Check this file periodically for updates

## Contact & Questions

This is a personal wedding planning tool. For questions about:

- **OpenAI data handling**: Contact OpenAI support or review their privacy policy
- **Pinterest data handling**: Contact Pinterest support or review their privacy policy
- **Local tool usage**: Refer to the README.md and documentation in this repository

## Summary

This wedding planning OCR pipeline is designed with **privacy by design** principles:

- ✅ **Local-first processing** minimizes external data sharing
- ✅ **Purpose limitation** focuses only on wedding planning needs
- ✅ **User control** keeps you in control of your data
- ✅ **Transparency** about what data is processed and how
- ✅ **Security measures** protect your information throughout the process

Your wedding planning data is yours. This tool helps you organize it while keeping it secure and private.

---

*Last updated: October 5, 2025*  
*Version: 1.0*