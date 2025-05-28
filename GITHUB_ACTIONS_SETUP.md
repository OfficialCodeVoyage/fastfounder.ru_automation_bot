# 🔧 GitHub Actions Setup Guide

Complete step-by-step guide to set up automated daily FastFounder analysis with GitHub Actions.

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ GitHub repository with the FastFounder bot code
- ✅ OpenAI API account with credits
- ✅ Telegram bot created
- ✅ FastFounder.ru account

## 🔐 Step 1: Configure GitHub Secrets

You need to add **5 secrets** to your GitHub repository:

### 1.1 Navigate to Secrets
1. **Go to your repository** on GitHub
2. **Click "Settings"** (top menu bar)
3. **Click "Secrets and variables"** → **"Actions"** (left sidebar)
4. **Click "New repository secret"**

### 1.2 Add Required Secrets

| Secret Name | Value | Where to Get It |
|-------------|-------|-----------------|
| `OPENAI_API_KEY` | Your OpenAI API key | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `TELEGRAM_TOKEN` | Your Telegram bot token | Message [@BotFather](https://t.me/botfather) |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | Message [@userinfobot](https://t.me/userinfobot) |
| `FAST_FOUNDER_EMAIL` | `bondarenkopavloua@yahoo.com` | Your FastFounder account |
| `FAST_FOUNDER_PASSWORD` | `MN[9[Bca5H<!X+fd` | Your FastFounder password |

### 1.3 How to Get Each Secret

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Click **"Create new secret key"**
3. Copy the key (starts with `sk-proj-...`)
4. **Important**: Ensure you have credits in your account

#### Telegram Bot Token
1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow prompts to create your bot
4. Copy the token (format: `123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

#### Telegram Chat ID
1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. Copy your chat ID (format: `123456789` or `-1001234567890` for groups)

#### FastFounder Credentials
- Use your existing FastFounder.ru login credentials
- Verify you can access full articles when logged in

## ⚡ Step 2: Enable GitHub Actions

### 2.1 Navigate to Actions
1. **Go to the "Actions" tab** in your repository
2. If you see a message about workflows, **click "I understand my workflows, go ahead and enable them"**

### 2.2 Verify Workflow
You should see your workflow: **"FastFounder Daily Digest (Authenticated)"**

## 🧪 Step 3: Test the Workflow

### 3.1 Manual Test Run
1. **In the Actions tab**, click on **"FastFounder Daily Digest (Authenticated)"**
2. **Click "Run workflow"** (right side, blue button)
3. **Click the green "Run workflow" button**
4. **Wait for completion** (should take 2-3 minutes)

### 3.2 Monitor the Run
- Watch the workflow progress in real-time
- Click on the running job to see detailed logs
- Look for success indicators:
  - ✅ Green checkmark when complete
  - 🔐 Authentication attempt logged
  - 📱 Telegram message sent

### 3.3 Verify Results
**Check your Telegram** for a message like:
```
🌅 FastFounder Daily • [Date]

🔥 [Score]/10 • [Article Title]

[AI Analysis...]

🔐 Полный контент (аутентификация)
🤖 Автоматически сгенерировано FastFounder Bot
```

## 📅 Step 4: Verify Automatic Schedule

Your workflow is configured to run automatically:
- **Time**: Daily at 9:15 AM Denver time (15:15 UTC)
- **Frequency**: Every day without manual intervention
- **Content**: Latest FastFounder article with full AI analysis

### Schedule Details
```yaml
schedule:
  # Run daily at 9:15 AM Denver time (15:15 UTC)
  - cron: '15 15 * * *'
```

## 🔍 Monitoring Your Bot

### Check Workflow Runs
- **Go to Actions tab** to see all runs
- **Click on any run** to see detailed logs
- **Green checkmark** = success, **red X** = failure

### Expected Telegram Message Format
```
🌅 FastFounder Daily • 27.05.2025

🔥 8/10 • Простой способ откусить кусочек огромных бюджетов

В этом обзоре ты узнаешь об эффективных стратегиях работы с крупными 
рекламными бюджетами в фармацевтической индустрии...

📊 Практичность: 8/10 | Новизна: 8/10 | Глубина: 8/10 | Актуальность: 8/10

🎯 Категория: Маркетинг
👥 Для кого: опытные бизнесмены • инвесторы

📋 План действий:
   ✅ Проанализировать фармацевтический рынок
   ✅ Изучить образовательные платформы для врачей

🔗 https://fastfounder.ru/article-url/

🔐 Полный контент (аутентификация)
🤖 Автоматически сгенерировано FastFounder Bot
```

## 🆘 Troubleshooting

### Common Issues and Solutions

#### 1. "Secret not found" Error
**Problem**: Workflow fails with missing secrets
**Solution**: 
- Double-check all 5 secrets are added with exact names
- Ensure no extra spaces in secret values
- Verify secret names match exactly: `OPENAI_API_KEY`, `TELEGRAM_TOKEN`, etc.

#### 2. "Authentication failed" Error
**Problem**: Can't log into FastFounder
**Solution**:
- Verify credentials work by logging in manually at FastFounder.ru
- Check for special characters in password
- Bot will fallback to public scraping if auth fails

#### 3. "No Telegram message" Error
**Problem**: Workflow runs but no message received
**Solution**:
- Test bot token by messaging your bot directly
- Verify chat ID is correct (use [@userinfobot](https://t.me/userinfobot))
- Check if bot is blocked or chat ID changed

#### 4. "OpenAI API error" Error
**Problem**: AI analysis fails
**Solution**:
- Check you have credits in OpenAI account
- Verify API key is active and correct
- Check OpenAI service status

#### 5. Workflow Doesn't Run Automatically
**Problem**: No daily messages
**Solution**:
- Verify workflow is enabled in Actions tab
- Check if repository has Actions enabled
- Ensure cron schedule is correct (15:15 UTC = 9:15 AM Denver)

### Debug Steps

#### Check Workflow Logs
1. Go to **Actions** → **Latest run**
2. Click on **"send-daily-digest"** job
3. Expand each step to see detailed logs
4. Look for error messages or authentication status

#### Test Individual Components
```bash
# Test locally first
python3 main_authenticated.py

# Check if secrets are accessible (in workflow)
echo "Testing secret access..."
if [ -z "$OPENAI_API_KEY" ]; then echo "❌ OPENAI_API_KEY missing"; fi
if [ -z "$TELEGRAM_TOKEN" ]; then echo "❌ TELEGRAM_TOKEN missing"; fi
```

## 🎉 Success Indicators

### ✅ Everything Working Correctly:
- ✅ Workflow runs without errors (green checkmark)
- ✅ Daily Telegram messages received at 9:15 AM Denver time
- ✅ Messages show "🔐 Полный контент (аутентификация)"
- ✅ AI analysis scores consistently 7-9/10
- ✅ Content length 7,000+ characters
- ✅ Specific action items and recommendations included

### 📊 Expected Results with Authentication:
- **Content Quality**: Complete articles (7,000+ characters)
- **Analysis Depth**: Comprehensive insights and recommendations
- **Scores**: Higher quality ratings (7-9/10 vs 2-4/10 without auth)
- **Action Items**: Specific, actionable business advice
- **Categories**: Accurate business category classification

## 🔄 Maintenance

### Regular Checks
- **Weekly**: Verify messages are still arriving
- **Monthly**: Check OpenAI credit balance
- **Quarterly**: Update dependencies if needed

### Updating Credentials
If you need to change any credentials:
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click on the secret name
3. Click **"Update"**
4. Enter new value and save

## 📞 Getting Help

### Documentation
- 📖 [AUTHENTICATION_SETUP.md](AUTHENTICATION_SETUP.md) - Detailed authentication setup
- 📋 [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Quick deployment checklist
- 📚 [README.md](README.md) - Complete project documentation

### Support Channels
- 🐛 [GitHub Issues](https://github.com/OfficialCodeVoyage/fastfounder_automation_bot/issues) - Report bugs
- 💬 [GitHub Discussions](https://github.com/OfficialCodeVoyage/fastfounder_automation_bot/discussions) - Ask questions
- 📧 Create an issue with logs for personalized help

---

**🚀 Your FastFounder Daily Bot is ready to deliver premium business insights automatically!** 