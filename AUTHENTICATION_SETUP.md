# FastFounder Authentication Setup

This enhanced version of the FastFounder Daily Bot includes authentication support to access full article content behind the paywall.

## Overview

The authenticated version provides:
- **Full article content** (6,000-8,000+ characters vs 1,000 characters without auth)
- **Better AI analysis** due to complete context
- **Higher quality scores** from comprehensive content understanding

## Setup Instructions

### 1. Environment Variables

Add these credentials to your `.env` file:

```bash
# Existing variables
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# FastFounder credentials
FAST_FOUNDER_EMAIL=your_fastfounder_email
FAST_FOUNDER_PASSWORD=your_fastfounder_password
```

### 2. GitHub Actions Setup

Add these secrets to your GitHub repository:
1. Go to Settings → Secrets and variables → Actions
2. Add all 5 secrets:
   - `OPENAI_API_KEY`
   - `TELEGRAM_TOKEN` 
   - `TELEGRAM_CHAT_ID`
   - `FAST_FOUNDER_EMAIL`
   - `FAST_FOUNDER_PASSWORD`

### 3. Deployment

Deploy using the authenticated workflow:

```bash
# Test locally
python3 main_authenticated.py

# Deploy to GitHub
git add .
git commit -m "Add authenticated FastFounder bot"
git push origin main
```

The bot will run daily at 9:15 AM Denver time via GitHub Actions.

## Authentication Status

✅ **Authentication is now working!** The bot successfully:
- Logs into FastFounder using WordPress authentication
- Accesses full article content (6,000+ characters)
- Provides comprehensive AI analysis of complete articles
- Falls back gracefully if authentication fails

## Content Comparison

| Source | Characters | Quality |
|--------|------------|---------|
| RSS Only | 300-400 | Basic preview |
| Public Scraping | 1,000 | Partial content (up to paywall) |
| **Authenticated** | **6,000-8,000+** | **Full article content** |

## Troubleshooting

### Authentication Issues

1. **Invalid credentials**: Check email/password in `.env` file
2. **Login page redirect**: Ensure credentials are correct
3. **Session timeout**: Bot creates new session for each run

### Content Extraction

The bot intelligently extracts content by:
1. Attempting authenticated access first
2. Falling back to public content if auth fails
3. Using RSS description as last resort

### Telegram Messages

Each message shows the content source:
- 🔐 Полный контент (аутентификация) - Full authenticated content
- 📄 Полный контент (до paywall) - Content up to paywall
- 📄 RSS контент - RSS preview only

## Security Notes

- Credentials are stored securely in environment variables
- No credentials are logged or exposed
- GitHub Actions secrets are encrypted
- Sessions are not persisted between runs

## Migration from Basic Version

To migrate from `main.py` to `main_authenticated.py`:

1. Add FastFounder credentials to `.env` and GitHub secrets
2. Update workflow to use `main_authenticated.py`
3. Remove old `main.py` and `daily-digest.yml` if desired
4. Commit and push changes

The authenticated version is backward compatible - it will work without credentials but with limited content access. 