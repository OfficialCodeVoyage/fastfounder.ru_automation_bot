# FastFounder Daily Bot - Multi-User Edition

🤖 **Automated daily digest bot for FastFounder articles with AI analysis and multi-user support**

## 🌟 Features

- **📡 RSS Feed Monitoring** - Automatically fetches latest FastFounder articles
- **🔐 Authenticated Content Access** - Full article content with FastFounder credentials
- **🤖 AI-Powered Analysis** - Comprehensive article analysis using GPT-4o mini
- **👥 Multi-User Support** - Broadcast to unlimited subscribers
- **📱 Telegram Integration** - Beautiful formatted messages with emojis
- **⚡ GitHub Actions Ready** - Runs daily without 24/7 server
- **🔄 Auto User Management** - Automatic user registration via `/start` command

## 📊 What Users Get

Each daily digest includes:
- **📈 Comprehensive Scoring** - 10-point scale analysis
- **🎯 Detailed Metrics** - Practicality, novelty, depth, relevance
- **👥 Target Audience** - Who should read this
- **⏱️ Reading Time** - How long it takes to study
- **💰 ROI Potential** - Expected return on investment
- **📋 Action Checklist** - Concrete steps to apply
- **⚠️ Risk Assessment** - Potential pitfalls to avoid
- **🏢 Business Stage** - Ideal for which stage of business

## 🚀 Quick Start

### 1. Setup Environment Variables

```bash
# Required
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key

# Optional (for full content access)
FAST_FOUNDER_EMAIL=your_fastfounder_email
FAST_FOUNDER_PASSWORD=your_fastfounder_password
```

### 2. Add Your First User

```bash
python add_user_manually.py
```

Enter your Telegram Chat ID (get it from [@userinfobot](https://t.me/userinfobot))

### 3. Test the Bot

```bash
python main_multiuser_daily.py
```

You should receive a daily digest!

### 4. Deploy to GitHub Actions

Replace your existing workflow file with:

```yaml
name: FastFounder Daily Digest

on:
  schedule:
    - cron: '0 6 * * *'  # 9:00 AM Moscow time
  workflow_dispatch:

jobs:
  send-digest:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Run FastFounder Bot
      env:
        TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        FAST_FOUNDER_EMAIL: ${{ secrets.FAST_FOUNDER_EMAIL }}
        FAST_FOUNDER_PASSWORD: ${{ secrets.FAST_FOUNDER_PASSWORD }}
      run: python main_multiuser_daily.py
```

## 👥 How Users Subscribe

### Option 1: Automatic (Recommended)
1. Users send `/start` to your bot anytime
2. Next day when bot runs, they get automatically added
3. They receive welcome message + daily digest

### Option 2: Manual Addition
1. User sends you their Chat ID
2. You run `python add_user_manually.py`
3. Add them manually

## 🛠️ User Management

### View All Users
```bash
python add_user_manually.py
# Choose option 2: List users
```

### Add User Manually
```bash
python add_user_manually.py
# Choose option 1: Add user
```

### Remove User
```bash
python add_user_manually.py
# Choose option 3: Remove user
```

### Check User Count
```bash
python -c "
from user_manager import UserManager
um = UserManager()
print(f'Active users: {um.get_user_count()}')
"
```

## 📁 Project Structure

```
fastfounder-daily/
├── main_multiuser_daily.py    # Main bot script (multi-user)
├── user_manager.py            # User management system
├── add_user_manually.py       # Manual user management tool
├── users.json                 # User database (auto-created)
├── README.md                  # This file
└── SIMPLE_MULTIUSER_SETUP.md  # Quick setup guide
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_TOKEN` | ✅ | Your Telegram bot token |
| `OPENAI_API_KEY` | ✅ | OpenAI API key for analysis |
| `FAST_FOUNDER_EMAIL` | ❌ | FastFounder account email |
| `FAST_FOUNDER_PASSWORD` | ❌ | FastFounder account password |

### Content Access Levels

1. **🔐 Authenticated** - Full article content (requires credentials)
2. **📄 RSS Content** - Article summary from RSS feed
3. **🔄 Fallback** - Basic content extraction

## 📱 Bot Commands

Users can interact with your bot using these commands:

- `/start` - Subscribe to daily digests
- `/help` - Show available commands (if implemented)

## 🔄 Daily Workflow

Every day at 9:00 AM Moscow time:

1. **👥 Check for new users** - Scans for `/start` messages
2. **➕ Add new subscribers** - Automatically registers them
3. **💌 Send welcome messages** - To new users only
4. **📡 Fetch latest article** - From FastFounder RSS
5. **🤖 Generate AI analysis** - Comprehensive scoring
6. **📱 Broadcast to all** - Send to all active users
7. **📊 Track delivery** - Monitor success/failure rates

## 🎯 AI Analysis Features

### Scoring Metrics (1-10 scale)
- **🎯 Practicality** - How applicable in practice
- **✨ Novelty** - How fresh/new the information is
- **🔍 Depth** - How thoroughly the topic is covered
- **⏰ Relevance** - How current/timely the content is

### Content Classification
- **📂 Category** - Strategy, marketing, sales, finance, tech, etc.
- **👥 Target Audience** - Beginners, experienced, marketers, etc.
- **⏱️ Reading Time** - Quick (5-10min), medium (15-30min), long (1+ hour)
- **🎚️ Complexity** - Simple, medium, complex
- **💰 ROI Potential** - High, medium, low
- **🏢 Business Stage** - Idea, launch, growth, scaling

## 🔍 Monitoring & Analytics

### User Statistics
- Total active users
- Message delivery success rate
- User join/leave tracking
- Message count per user

### Content Quality Tracking
- Authentication success rate
- Content extraction quality
- AI analysis success rate
- Fallback usage statistics

## 🚨 Error Handling

The bot gracefully handles:
- **🔐 Authentication failures** - Falls back to RSS content
- **🤖 AI API errors** - Uses fallback analysis
- **📱 Telegram delivery failures** - Logs and continues
- **🚫 Blocked users** - Automatically removes them
- **📡 RSS feed issues** - Retries and logs errors

## 🔧 Troubleshooting

### Common Issues

**No users receiving messages:**
```bash
# Check if you have active users
python -c "from user_manager import UserManager; print(UserManager().get_user_count())"
```

**Authentication not working:**
- Verify `FAST_FOUNDER_EMAIL` and `FAST_FOUNDER_PASSWORD`
- Check if credentials work on fastfounder.ru website

**AI analysis failing:**
- Verify `OPENAI_API_KEY` is valid
- Check OpenAI API quota/billing

**Telegram messages not sending:**
- Verify `TELEGRAM_TOKEN` is correct
- Test with: `curl -X GET "https://api.telegram.org/bot<TOKEN>/getMe"`

## 📈 Scaling

The bot can handle:
- **Unlimited users** - No hard limits
- **Daily execution** - Optimized for GitHub Actions
- **Automatic cleanup** - Removes blocked/inactive users
- **Efficient broadcasting** - Parallel message sending

## 🔒 Security

- **🔐 Credentials** - Stored as environment variables
- **📊 User data** - Minimal storage (chat ID, username, stats)
- **🚫 No personal data** - No message content stored
- **🔄 Auto cleanup** - Inactive users removed automatically

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Test individual components
4. Create an issue with detailed information

---

**🎉 Ready to get started? Run `python add_user_manually.py` to add your first user!**
