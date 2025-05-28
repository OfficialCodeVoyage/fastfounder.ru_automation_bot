# Simple Multi-User Setup for FastFounder Daily Bot

Since your bot runs **once daily via GitHub Actions** (not 24/7), here's the streamlined setup:

## 🎯 Quick Setup (3 Steps)

### Step 1: Add Your First User

```bash
python add_user_manually.py
```

Follow the prompts:
- Enter your Telegram Chat ID (get from [@userinfobot](https://t.me/userinfobot))
- Enter your username, name (optional)

### Step 2: Test the Bot

```bash
python main_multiuser_daily.py
```

You should receive a daily digest!

### Step 3: Deploy to GitHub Actions

The workflow file is already configured. Just add these secrets in GitHub:
- `TELEGRAM_TOKEN` (required)
- `OPENAI_API_KEY` (required)  
- `FAST_FOUNDER_EMAIL` (optional, for full content)
- `FAST_FOUNDER_PASSWORD` (optional, for full content)

## 📱 How Users Join

### Option A: Automatic (Recommended)
Users send `/start` to your bot anytime → They get added automatically next day

### Option B: Manual Addition
You run `python add_user_manually.py` and add their Chat ID

## 🔧 User Management

### View all users:
```bash
python add_user_manually.py
# Choose option 2: List users
```

### Add user manually:
```bash
python add_user_manually.py
# Choose option 1: Add user
```

### Remove user:
```bash
python add_user_manually.py
# Choose option 3: Remove user
```

## 📊 How It Works Daily

Every day at 9:00 AM Moscow time:

1. **👥 Check for new users** - Scans for `/start` messages
2. **➕ Add new users** - Automatically registers them  
3. **💌 Send welcome messages** - To new users only
4. **📡 Process article** - Gets latest FastFounder article
5. **🤖 Generate analysis** - AI analysis with scoring
6. **📱 Broadcast to all** - Sends to ALL active users

## ✅ Benefits

- ✅ **No 24/7 server needed** - Works with GitHub Actions
- ✅ **Automatic user detection** - Users can join anytime
- ✅ **Manual control** - You can add/remove users manually
- ✅ **Backward compatible** - Your existing setup still works
- ✅ **Scales easily** - Handles unlimited users

## 🚀 Tell Your Friends

Send them this message:

> "Send `/start` to @YourBotName to get daily FastFounder digests with AI analysis. You'll be added automatically and start receiving daily updates!"

## 🔍 Check Status

```bash
python -c "
from user_manager import UserManager
um = UserManager()
print(f'Active users: {um.get_user_count()}')
for chat_id in um.get_active_users():
    user = um.get_user_info(chat_id)
    print(f'  {chat_id}: {user.get(\"first_name\", \"Unknown\")}')
"
```

## ❓ FAQ

**Q: What if someone sends `/start` and I don't run the bot for a week?**
A: They'll be added the next time the bot runs and get a welcome message.

**Q: Can users unsubscribe?**
A: Not automatically with daily-only execution. You'd need to remove them manually.

**Q: Will this work with my current GitHub Actions?**
A: Yes! The workflow file is already updated.

**Q: What if I want to go back to single-user?**
A: Just modify the main script to use a single chat ID instead of broadcasting.

This approach gives you multi-user functionality while keeping your simple daily GitHub Actions setup! 🎉 