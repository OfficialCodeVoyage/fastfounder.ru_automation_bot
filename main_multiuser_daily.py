#!/usr/bin/env python3
"""
FastFounder Daily Link-Push Bot - Multi-User Daily Version

Enhanced version with multi-user support for daily GitHub Actions execution.
Checks for new users and broadcasts daily digests to all subscribed users.
"""

import json
import os
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import xml.etree.ElementTree as ET
from html import unescape
import re
import logging
import sys
from datetime import datetime
from user_manager import UserManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_for_new_users():
    """Check for new users who sent /start since last run."""
    logger.info("👥 Checking for new users...")
    
    telegram_token = os.environ.get('TELEGRAM_TOKEN')
    if not telegram_token:
        logger.warning("⚠️ No Telegram token found, skipping user check")
        return
    
    user_manager = UserManager()
    
    try:
        # Get recent updates from Telegram
        url = f"https://api.telegram.org/bot{telegram_token}/getUpdates"
        params = {'limit': 100}  # Get last 100 updates
        
        url_with_params = f"{url}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url_with_params) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if not result.get('ok'):
            logger.error(f"❌ Failed to get updates: {result}")
            return
        
        updates = result.get('result', [])
        new_users_count = 0
        
        for update in updates:
            if 'message' in update:
                message = update['message']
                text = message.get('text', '')
                
                if text.startswith('/start'):
                    chat_id = message['chat']['id']
                    user = message.get('from', {})
                    
                    username = user.get('username')
                    first_name = user.get('first_name')
                    last_name = user.get('last_name')
                    
                    # Check if user already exists
                    existing_user = user_manager.get_user_info(str(chat_id))
                    if not existing_user or not existing_user.get('active', False):
                        user_manager.add_user(chat_id, username, first_name, last_name)
                        new_users_count += 1
                        logger.info(f"👤 Added new user: {chat_id}")
                        
                        # Send welcome message
                        send_welcome_message(chat_id, first_name, telegram_token)
        
        if new_users_count > 0:
            total_users = user_manager.get_user_count()
            logger.info(f"🎉 Added {new_users_count} new users! Total: {total_users}")
        else:
            logger.info("📊 No new users found")
            
    except Exception as e:
        logger.error(f"❌ Error checking for new users: {e}")


def send_welcome_message(chat_id, first_name, telegram_token):
    """Send welcome message to new user."""
    welcome_message = f"""🎉 <b>Добро пожаловать в FastFounder Daily!</b>

Привет{f', {first_name}' if first_name else ''}! 👋

Теперь ты будешь получать ежедневные дайджесты с лучшими статьями от FastFounder с подробным AI-анализом:

📊 <b>Что ты получишь:</b>
• Оценка статей по 10-балльной шкале
• Детальный анализ практичности, новизны и глубины
• Конкретные действия для применения
• Оценка рисков и ROI потенциала
• Время изучения и сложность материала

🕐 <b>Когда:</b> Каждый день в 9:00 МСК

<i>🤖 Powered by AI • FastFounder Daily Bot</i>"""
    
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        
        data = {
            'chat_id': chat_id,
            'text': welcome_message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data=encoded_data)
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('ok'):
                logger.info(f"✅ Welcome message sent to {chat_id}")
            else:
                logger.error(f"❌ Failed to send welcome message to {chat_id}: {result}")
                
    except Exception as e:
        logger.error(f"❌ Error sending welcome message to {chat_id}: {e}")


class FastFounderAuthenticatedScraper:
    """Authenticated scraper for FastFounder articles."""
    
    def __init__(self):
        # Set up cookie jar for session management
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        
        # Add headers to mimic a real browser
        self.opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('Accept-Language', 'ru-RU,ru;q=0.9,en;q=0.8'),
            ('Connection', 'keep-alive'),
            ('Upgrade-Insecure-Requests', '1'),
        ]
        
        # Install the opener
        urllib.request.install_opener(self.opener)
        
        self.logged_in = False
        
    def login(self, email, password):
        """Login to FastFounder."""
        logger.info("🔐 Attempting to login to FastFounder...")
        
        try:
            # First, get the login page to extract any CSRF tokens or form data
            login_page_url = "https://fastfounder.ru/wp-login.php"
            
            req = urllib.request.Request(login_page_url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req) as response:
                login_page_data = response.read()
                try:
                    login_page_html = login_page_data.decode('utf-8')
                except UnicodeDecodeError:
                    login_page_html = login_page_data.decode('utf-8', errors='ignore')
            
            # Prepare login data - using the correct WordPress form fields
            login_data = {
                'log': email,  # Username or email field
                'pwd': password,  # Password field
                'wp-submit': 'Войти',  # Submit button
                'redirect_to': 'https://fastfounder.ru/',  # Redirect after login
                'testcookie': '1',
                'rememberme': 'forever'  # Remember me checkbox
            }
            
            # Encode the data
            encoded_data = urllib.parse.urlencode(login_data).encode('utf-8')
            
            # Create the request
            login_request = urllib.request.Request(
                "https://fastfounder.ru/wp-login.php",
                data=encoded_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': 'https://fastfounder.ru/wp-login.php',
                    'Origin': 'https://fastfounder.ru'
                }
            )
            
            # Submit login
            with urllib.request.urlopen(login_request) as response:
                login_response_data = response.read()
                try:
                    login_response = login_response_data.decode('utf-8')
                except UnicodeDecodeError:
                    login_response = login_response_data.decode('utf-8', errors='ignore')
                response_url = response.geturl()
            
            logger.info(f"📍 Login response URL: {response_url}")
            
            # Check if login was successful
            if 'wp-login.php' not in response_url and 'loggedout' not in response_url:
                logger.info("✅ Login successful!")
                self.logged_in = True
                return True
            else:
                logger.error("❌ Login failed - redirected back to login page")
                if 'loggedout=true' in response_url:
                    logger.info("🔍 System indicates we were logged out")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def get_full_article_content(self, article_url):
        """Get full article content using authenticated session."""
        if not self.logged_in:
            logger.error("❌ Not logged in! Cannot access full content.")
            return None
        
        logger.info(f"📖 Fetching full authenticated article content...")
        
        try:
            with urllib.request.urlopen(article_url) as response:
                html_content = response.read().decode('utf-8')
            
            # Extract clean content
            clean_content = self._extract_clean_content(html_content)
            
            logger.info(f"✅ Extracted {len(clean_content)} characters of authenticated content")
            return clean_content
            
        except Exception as e:
            logger.error(f"❌ Error fetching authenticated article: {e}")
            return None
    
    def _extract_clean_content(self, html_content):
        """Extract clean article content from HTML."""
        
        # Remove script tags and their content
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove style tags and their content
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove comments
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
        
        # Convert to text
        text_content = re.sub(r'<[^>]+>', ' ', html_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        return text_content


def get_rss_feed():
    """Fetch and parse RSS feed."""
    logger.info("📡 Fetching RSS feed...")
    
    try:
        rss_url = "https://fastfounder.ru/feed/"
        
        with urllib.request.urlopen(rss_url) as response:
            rss_data = response.read()
        
        # Parse XML
        root = ET.fromstring(rss_data)
        
        articles = []
        
        # Find all items in the RSS feed
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem = item.find('link')
            description_elem = item.find('description')
            pub_date_elem = item.find('pubDate')
            
            if title_elem is not None and link_elem is not None:
                article = {
                    'title': unescape(title_elem.text or ''),
                    'url': link_elem.text or '',
                    'description': unescape(description_elem.text or '') if description_elem is not None else '',
                    'pub_date': pub_date_elem.text or '' if pub_date_elem is not None else ''
                }
                articles.append(article)
        
        logger.info(f"✅ Found {len(articles)} articles in RSS feed")
        return articles
        
    except Exception as e:
        logger.error(f"❌ Error fetching RSS feed: {e}")
        return []


def scrape_article_content_authenticated(article, scraper):
    """Scrape article content with authentication support."""
    logger.info(f"🔍 Scraping article: {article['title']}")
    
    # Start with RSS description
    content = article.get('description', '')
    content_quality = 'rss'
    
    # Try to get full content if authenticated
    if scraper and scraper.logged_in:
        try:
            full_content = scraper.get_full_article_content(article['url'])
            if full_content and len(full_content) > len(content):
                content = full_content
                content_quality = 'authenticated'
                logger.info(f"✅ Using authenticated content ({len(content)} chars)")
        except Exception as e:
            logger.warning(f"⚠️ Failed to get authenticated content: {e}")
    
    # Clean and prepare content
    clean_content = minimal_clean(content)
    
    # Create article data
    article_data = {
        'title': article['title'],
        'url': article['url'],
        'content': clean_content,
        'content_quality': content_quality,
        'pub_date': article.get('pub_date', ''),
        'description': article.get('description', '')
    }
    
    logger.info(f"📄 Article content prepared: {len(clean_content)} characters")
    return article_data


def minimal_clean(content):
    """Minimal content cleaning."""
    if not content:
        return ""
    
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', ' ', content)
    
    # Clean up whitespace
    content = re.sub(r'\s+', ' ', content).strip()
    
    # Remove common unwanted phrases
    unwanted_phrases = [
        'Читать далее',
        'Подробнее',
        'Источник:',
        'Поделиться:',
        'Теги:',
        'Категории:'
    ]
    
    for phrase in unwanted_phrases:
        content = content.replace(phrase, '')
    
    return content.strip()


def generate_enhanced_analysis(article):
    """Generate enhanced AI analysis of the article."""
    logger.info("🤖 Generating enhanced AI analysis...")
    
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        logger.error("❌ OpenAI API key not found")
        return create_fallback_analysis(article)
    
    # Prepare content for analysis
    content_for_analysis = f"""
Заголовок: {article['title']}
Контент: {article['content'][:8000]}
URL: {article['url']}
"""
    
    # Enhanced prompt for comprehensive analysis
    prompt = f"""Проанализируй эту статью с FastFounder и создай подробный обзор в формате:

в этом обзоре ты узнаешь об [краткое описание темы], и вот наша оценка данного поста + добавь идеи как я могу использовать это каждый день

Также предоставь детальную оценку по следующим критериям (каждый от 1 до 10):
- Практичность (насколько применимо на практике)
- Новизна (насколько новая/свежая информация)
- Глубина (насколько глубоко раскрыта тема)
- Актуальность (насколько актуально сейчас)

Определи:
- Категорию (стратегия, маркетинг, продажи, финансы, технологии, личная эффективность, аналитика)
- Целевую аудиторию (новички, опытные, маркетологи, IT, фрилансеры, инвесторы, студенты)
- Время изучения (быстрое 5-10мин, среднее 15-30мин, долгое 1+ час)
- Сложность (простой, средний, сложный)
- ROI потенциал (высокий, средний, низкий)
- Стадию бизнеса (идея, запуск, рост, масштабирование)
- Время до результата (неделя, месяц, квартал, год)

Создай 3-5 конкретных действий для применения
Укажи 2-3 основных риска
Дай общую оценку от 1 до 10 с объяснением

Статья:
{content_for_analysis}

Ответь в формате JSON:
{{
    "summary": "в этом обзоре ты узнаешь об...",
    "overall_score": число от 1 до 10,
    "scores": {{
        "practicality": число,
        "novelty": число,
        "depth": число,
        "relevance": число
    }},
    "category": "категория",
    "target_audience": ["аудитория1", "аудитория2"],
    "reading_time": "время",
    "complexity_level": "уровень",
    "roi_potential": "потенциал",
    "business_stage": "стадия",
    "result_timeframe": "время",
    "action_checklist": ["действие1", "действие2", "действие3"],
    "main_risks": ["риск1", "риск2"],
    "score_reason": "объяснение оценки"
}}"""
    
    try:
        # Prepare OpenAI API request
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты эксперт по анализу бизнес-контента. Отвечай только в формате JSON без дополнительного текста."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        json_data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=json_data, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content'].strip()
            
            # Try to parse JSON response
            try:
                # Remove any markdown formatting
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                
                analysis_data = json.loads(content)
                
                # Validate the response
                if validate_enhanced_analysis(analysis_data, article):
                    logger.info("✅ Enhanced AI analysis generated successfully")
                    return analysis_data
                else:
                    logger.warning("⚠️ AI analysis validation failed, using fallback")
                    return create_fallback_analysis(article)
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse AI response as JSON: {e}")
                logger.error(f"Raw response: {content}")
                return create_fallback_analysis(article)
        else:
            logger.error("❌ No valid response from OpenAI")
            return create_fallback_analysis(article)
            
    except Exception as e:
        logger.error(f"❌ Error calling OpenAI API: {e}")
        return create_fallback_analysis(article)


def validate_enhanced_analysis(data, article):
    """Validate the enhanced analysis data."""
    required_fields = [
        'summary', 'overall_score', 'scores', 'category', 'target_audience',
        'reading_time', 'complexity_level', 'roi_potential', 'business_stage',
        'result_timeframe', 'action_checklist', 'main_risks', 'score_reason'
    ]
    
    for field in required_fields:
        if field not in data:
            logger.error(f"❌ Missing required field: {field}")
            return False
    
    # Validate scores
    if not isinstance(data['overall_score'], (int, float)) or not (1 <= data['overall_score'] <= 10):
        logger.error("❌ Invalid overall_score")
        return False
    
    # Add title if missing
    if 'title' not in data:
        data['title'] = article['title']
    
    return True


def create_fallback_analysis(article):
    """Create a fallback analysis when AI fails."""
    logger.info("🔄 Creating fallback analysis...")
    
    return {
        "title": article['title'],
        "summary": f"в этом обзоре ты узнаешь об интересной теме из мира бизнеса и стартапов, и вот наша оценка данного поста + рекомендуем изучить материал для расширения кругозора",
        "overall_score": 6,
        "scores": {
            "practicality": 6,
            "novelty": 6,
            "depth": 6,
            "relevance": 6
        },
        "category": "стратегия",
        "target_audience": ["новички", "опытные"],
        "reading_time": "среднее 15-30мин",
        "complexity_level": "средний",
        "roi_potential": "средний",
        "business_stage": "любая",
        "result_timeframe": "месяц",
        "action_checklist": [
            "Изучить материал полностью",
            "Выделить ключевые моменты",
            "Подумать о применении в своем проекте"
        ],
        "main_risks": [
            "Информация может быть неполной",
            "Требуется дополнительная проверка"
        ],
        "score_reason": "Автоматическая оценка. Рекомендуем изучить материал самостоятельно."
    }


def get_score_emoji(score):
    """Get emoji based on score."""
    if score >= 9:
        return "🔥"
    elif score >= 8:
        return "⭐️"
    elif score >= 7:
        return "👍"
    elif score >= 6:
        return "👌"
    elif score >= 5:
        return "🤔"
    else:
        return "😐"


def get_category_emoji(category):
    """Get emoji for category."""
    category_emojis = {
        'стратегия': '🎯',
        'маркетинг': '📈',
        'продажи': '💰',
        'финансы': '💳',
        'технологии': '💻',
        'личная эффективность': '⚡️',
        'аналитика': '📊'
    }
    return category_emojis.get(category.lower(), '📝')


def get_complexity_emoji(complexity):
    """Get emoji for complexity level."""
    if 'простой' in complexity.lower():
        return '🟢'
    elif 'средний' in complexity.lower():
        return '🟡'
    else:
        return '🔴'


def get_roi_emoji(roi):
    """Get emoji for ROI potential."""
    if 'высокий' in roi.lower():
        return '💎'
    elif 'средний' in roi.lower():
        return '💰'
    else:
        return '🪙'


def broadcast_telegram_message(article, analysis, user_manager):
    """Broadcast enhanced message to all subscribed users."""
    logger.info("📱 Broadcasting enhanced Telegram message to all users...")
    
    telegram_token = os.environ.get('TELEGRAM_TOKEN')
    
    if not telegram_token:
        logger.error("❌ Telegram token not found")
        return False
    
    # Get all active users
    active_users = user_manager.get_active_users()
    
    if not active_users:
        logger.warning("⚠️ No active users found")
        return False
    
    logger.info(f"📊 Broadcasting to {len(active_users)} users")
    
    # Get current date
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    # Get emojis
    score_emoji = get_score_emoji(analysis['overall_score'])
    category_emoji = get_category_emoji(analysis['category'])
    complexity_emoji = get_complexity_emoji(analysis['complexity_level'])
    roi_emoji = get_roi_emoji(analysis['roi_potential'])
    
    # Format target audience
    audience_text = ' • '.join(analysis['target_audience'])
    
    # Format action checklist
    action_list = '\n'.join([f"   ✅ {action}" for action in analysis['action_checklist']])
    
    # Format risks
    risk_list = '\n'.join([f"   ⚠️ {risk}" for risk in analysis['main_risks']])
    
    # Content quality indicator
    content_indicator = ""
    if analysis.get('content_quality') == 'authenticated':
        content_indicator = "🔐 Полный контент (аутентификация)"
    elif analysis.get('content_quality') == 'full_extraction':
        content_indicator = "📄 Полный контент (до paywall)"
    elif analysis.get('content_quality') == 'improved_extraction':
        content_indicator = "📄 Расширенный контент (до paywall)"
    elif analysis.get('content_quality') == 'fallback':
        content_indicator = "⚠️ Частичный контент (публичный доступ)"
    else:
        content_indicator = "📄 RSS контент"
    
    # Create the message
    message = f"""🌅 <b>FastFounder Daily • {current_date}</b>

{score_emoji} <b>{analysis['overall_score']}/10</b> • {analysis['title']}

{analysis['summary']}

📊 <b>Практичность:</b> {analysis['scores']['practicality']}/10 | <b>Новизна:</b> {analysis['scores']['novelty']}/10 | <b>Глубина:</b> {analysis['scores']['depth']}/10 | <b>Актуальность:</b> {analysis['scores']['relevance']}/10

{category_emoji} <b>Категория:</b> {analysis['category'].title()}
👥 <b>Для кого:</b> {audience_text}
⏱ <b>Время изучения:</b> {analysis['reading_time']}

{complexity_emoji} <b>Сложность:</b> {analysis['complexity_level']}
{roi_emoji} <b>ROI потенциал:</b> {analysis['roi_potential']}
🏢 <b>Стадия бизнеса:</b> {analysis['business_stage']}
⏰ <b>Результат через:</b> {analysis['result_timeframe']}

📋 <b>План действий:</b>
{action_list}

⚠️ <b>Основные риски:</b>
{risk_list}

💡 <b>AI анализ:</b> {analysis['score_reason']}

🔗 {article['url']}

<i>{content_indicator}</i>
<i>🤖 Автоматически сгенерировано FastFounder Bot</i>"""
    
    # Send to all users
    successful_sends = 0
    failed_sends = 0
    
    for chat_id in active_users:
        try:
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')
            
            req = urllib.request.Request(url, data=encoded_data)
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('ok'):
                    successful_sends += 1
                    user_manager.increment_message_count(chat_id)
                    logger.info(f"✅ Message sent to {chat_id}")
                else:
                    failed_sends += 1
                    logger.error(f"❌ Failed to send to {chat_id}: {result}")
                    
                    # If user blocked the bot, deactivate them
                    if result.get('error_code') == 403:
                        user_manager.remove_user(chat_id)
                        logger.info(f"🚫 User {chat_id} blocked bot, deactivated")
                        
        except Exception as e:
            failed_sends += 1
            logger.error(f"❌ Error sending to {chat_id}: {e}")
    
    logger.info(f"📊 Broadcast complete: {successful_sends} successful, {failed_sends} failed")
    return successful_sends > 0


def main():
    """Main function with user check."""
    logger.info("🚀 Starting FastFounder Daily Bot (Multi-User Daily Version)")
    
    # Step 1: Check for new users first
    check_for_new_users()
    
    # Step 2: Initialize user manager
    user_manager = UserManager()
    
    # Check if we have any users
    active_users = user_manager.get_active_users()
    if not active_users:
        logger.warning("⚠️ No active users found. Add users manually or wait for /start messages.")
        return
    
    logger.info(f"📊 Broadcasting to {len(active_users)} active users")
    
    # Step 3: Initialize authenticated scraper
    scraper = None
    email = os.environ.get('FAST_FOUNDER_EMAIL')
    password = os.environ.get('FAST_FOUNDER_PASSWORD')
    
    if email and password:
        logger.info("🔐 Credentials found, initializing authenticated scraper...")
        scraper = FastFounderAuthenticatedScraper()
        if scraper.login(email, password):
            logger.info("✅ Authentication successful - will use full content")
        else:
            logger.warning("⚠️ Authentication failed - will use fallback scraping")
            scraper = None
    else:
        logger.warning("⚠️ No FastFounder credentials found - using fallback scraping")
    
    # Step 4: Get RSS feed
    articles = get_rss_feed()
    
    if not articles:
        logger.error("❌ No articles found in RSS feed")
        return
    
    # Step 5: Process the latest article
    article = articles[0]
    logger.info(f"📰 Processing article: {article['title']}")
    
    # Step 6: Scrape article content (authenticated or fallback)
    article_data = scrape_article_content_authenticated(article, scraper)
    
    # Step 7: Generate enhanced analysis
    analysis = generate_enhanced_analysis(article_data)
    
    # Step 8: Broadcast to all users
    success = broadcast_telegram_message(article_data, analysis, user_manager)
    
    if success:
        logger.info("🎉 Daily digest broadcast successfully!")
    else:
        logger.error("❌ Failed to broadcast daily digest")


if __name__ == "__main__":
    main() 