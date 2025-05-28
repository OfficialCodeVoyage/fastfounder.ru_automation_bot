#!/usr/bin/env python3
"""
FastFounder Daily Link-Push Bot - Authenticated Version

Enhanced version with authentication to access full article content.
Provides comprehensive analysis based on complete articles (11,000+ characters).
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


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
    
    def _test_authentication(self):
        """Test if we're properly authenticated."""
        try:
            test_url = "https://fastfounder.ru/"
            
            with urllib.request.urlopen(test_url) as response:
                test_content = response.read().decode('utf-8')
            
            # Look for indicators of being logged in
            logged_in_indicators = ['logout', 'выйти', 'profile', 'профиль', 'dashboard', 'account']
            
            if any(indicator in test_content.lower() for indicator in logged_in_indicators):
                logger.info("✅ Authentication confirmed!")
                self.logged_in = True
                return True
            else:
                logger.error("❌ Authentication failed")
                self.logged_in = False
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication test error: {e}")
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
        
        # Look for the article title and start from there
        title_patterns = [
            r'Простой способ откусить кусочек огромных бюджетов',
            r'Стартап получил \$80M',
            r'Опубликовано \d{2}\.\d{2}\.\d{4}',
        ]
        
        article_start = 0
        for pattern in title_patterns:
            match = re.search(pattern, text_content)
            if match:
                article_start = match.start()
                logger.info(f"📍 Found article start at '{pattern}' (position {article_start})")
                break
        
        # If no title found, look for content markers
        if article_start == 0:
            content_markers = [
                'Суть проекта',
                'VuMedi — это место',
                '#здоровье • #маркетинг',
                'Удивительно',
            ]
            
            for marker in content_markers:
                pos = text_content.find(marker)
                if pos != -1:
                    article_start = pos
                    logger.info(f"📍 Found content start at '{marker}' (position {pos})")
                    break
        
        # Look for the end of the article (before comments/footer)
        end_markers = [
            'Добавить комментарий',
            'Вы вошли как',
            '© Аркадий Морейнис',
            'ff@fastfounder.ru',
            'Публичная оферта'
        ]
        
        article_end = len(text_content)
        for marker in end_markers:
            pos = text_content.find(marker, article_start)
            if pos != -1 and pos < article_end:
                article_end = pos
                logger.info(f"📍 Found article end at '{marker}' (position {pos})")
                break
        
        # Extract the article content
        if article_start < article_end:
            clean_text = text_content[article_start:article_end].strip()
            logger.info(f"📄 Extracted article: {len(clean_text)} characters (from {article_start} to {article_end})")
        else:
            # Fallback: skip first 500 characters
            clean_text = text_content[500:].strip() if len(text_content) > 500 else text_content
            logger.info(f"📄 Fallback extraction: {len(clean_text)} characters")
        
        return clean_text


def get_rss_feed():
    """Get RSS feed items using only standard library."""
    logger.info("📡 Fetching RSS feed...")
    
    try:
        # Create request without gzip encoding
        req = urllib.request.Request("https://fastfounder.ru/feed/")
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        # Fetch the RSS feed
        with urllib.request.urlopen(req) as response:
            rss_data = response.read()
            
            # Try to decode with different encodings
            try:
                rss_text = rss_data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    rss_text = rss_data.decode('cp1251')
                except UnicodeDecodeError:
                    rss_text = rss_data.decode('utf-8', errors='ignore')
        
        # Parse XML
        root = ET.fromstring(rss_text)
        
        # Find all items
        items = []
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem = item.find('link')
            desc_elem = item.find('description')
            
            if title_elem is not None and link_elem is not None:
                title = unescape(title_elem.text or "")
                link = link_elem.text or ""
                description = unescape(desc_elem.text or "") if desc_elem is not None else ""
                
                # Clean up description (remove HTML tags)
                description = re.sub(r'<[^>]+>', '', description)
                description = description.strip()
                
                items.append({
                    'title': title,
                    'link': link,
                    'description': description
                })
        
        logger.info(f"✅ Found {len(items)} articles in RSS feed")
        return items[:1]  # Return only the latest article for daily digest
        
    except Exception as e:
        logger.error(f"❌ Error fetching RSS feed: {e}")
        return []


def scrape_article_content_authenticated(article, scraper):
    """Scrape full article content using authentication."""
    logger.info(f"🔍 Scraping authenticated article content: {article['title']}")
    
    # Try authenticated scraping first
    if scraper and scraper.logged_in:
        full_content = scraper.get_full_article_content(article['link'])
        if full_content and len(full_content) > 1000:
            return {
                'title': article['title'],
                'content': full_content,
                'url': article['link'],
                'description': article['description'],
                'content_source': 'authenticated'
            }
    
    # Direct content extraction - get everything before paywall
    logger.warning("⚠️ Extracting all content before paywall")
    try:
        req = urllib.request.Request(article['link'])
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
        
        # Extract ALL text content (minimal filtering)
        text_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text_content = re.sub(r'<style[^>]*>.*?</style>', '', text_content, flags=re.DOTALL | re.IGNORECASE)
        text_content = re.sub(r'<[^>]+>', ' ', text_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # Find paywall and take EVERYTHING before it
        paywall_indicators = [
            'читать дальше ➤ подпишись',
            'подпишись , чтобы увидеть полный текст',
            'подпишись, чтобы увидеть полный текст',
            'чтобы увидеть полный текст обзора',
        ]
        
        # Find the earliest paywall position
        paywall_pos = len(text_content)
        
        for indicator in paywall_indicators:
            pos = text_content.lower().find(indicator.lower())
            if pos != -1 and pos < paywall_pos:
                paywall_pos = pos
                logger.info(f"🔒 Paywall found at position {pos}: '{indicator}'")
        
        # Take all content before paywall
        if paywall_pos < len(text_content):
            content = text_content[:paywall_pos].strip()
            logger.info(f"✅ Extracted {len(content)} characters before paywall")
        else:
            content = text_content
            logger.info(f"✅ No paywall found, using all {len(content)} characters")
        
        # Minimal cleaning - just remove obvious junk at the start
        content = minimal_clean(content)
        
        return {
            'title': article['title'],
            'content': content,
            'url': article['link'],
            'description': article['description'],
            'content_source': 'full_extraction'
        }
        
    except Exception as e:
        logger.error(f"❌ Error scraping article: {e}")
        # Final fallback to RSS description
        return {
            'title': article['title'],
            'content': article['description'],
            'url': article['link'],
            'description': article['description'],
            'content_source': 'rss_only'
        }


def minimal_clean(content):
    """Minimal cleaning - just remove obvious technical junk."""
    # Skip to actual article content
    article_markers = [
        '1. Удивительно',
        'Удивительно',
        'самый быстрорастущий сегмент',
    ]
    
    for marker in article_markers:
        pos = content.find(marker)
        if pos != -1:
            logger.info(f"📍 Found article start at '{marker}' (position {pos})")
            # Include everything from this marker onwards
            return content[pos:].strip()
    
    # Fallback: look for date pattern and start from there
    date_pattern = re.search(r'Опубликовано \d{2}\.\d{2}\.\d{4}', content)
    if date_pattern:
        start_pos = date_pattern.end()
        logger.info(f"📍 Found date pattern, starting from position {start_pos}")
        return content[start_pos:].strip()
    
    # Last resort: skip first 400 chars of navigation/header
    if len(content) > 500:
        logger.info("📍 Using fallback: skipping first 400 characters")
        return content[400:].strip()
    
    return content


def generate_enhanced_analysis(article):
    """Generate enhanced comprehensive analysis using GPT-4o mini."""
    logger.info(f"🤖 Generating enhanced analysis for: {article['title']}")
    
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        logger.warning("❌ OpenAI API key not found, using fallback analysis")
        return create_fallback_analysis(article)
    
    # Adjust content length based on source
    content_for_analysis = article['content']
    if article.get('content_source') == 'authenticated':
        # Use more content for authenticated articles (up to 8000 chars)
        content_for_analysis = content_for_analysis[:8000]
        logger.info(f"📊 Using {len(content_for_analysis)} characters of authenticated content for analysis")
    elif article.get('content_source') == 'full_extraction':
        # Use substantial content for full extraction (up to 8000 chars)
        content_for_analysis = content_for_analysis[:8000]
        logger.info(f"📊 Using {len(content_for_analysis)} characters of full extraction content for analysis")
    elif article.get('content_source') == 'improved_extraction':
        # Use substantial content for improved extraction (up to 6000 chars)
        content_for_analysis = content_for_analysis[:6000]
        logger.info(f"📊 Using {len(content_for_analysis)} characters of improved extraction content for analysis")
    else:
        # Use standard amount for fallback content
        content_for_analysis = content_for_analysis[:3500]
        logger.info(f"📊 Using {len(content_for_analysis)} characters of fallback content for analysis")
    
    # Prepare the enhanced prompt
    prompt = f"""
    Проведи максимально детальный анализ следующей статьи и создай полную характеристику.
    
    Заголовок: {article['title']}
    
    Содержание:
    {content_for_analysis}
    
    ВАЖНО: Контент получен через {'аутентификацию (полная статья)' if article.get('content_source') == 'authenticated' else 'публичный доступ (может быть неполным)'}.
    
    ШКАЛЫ ОЦЕНКИ (1-10):
    - Практичность: насколько легко применить на практике
    - Новизна: уникальность и оригинальность идей
    - Глубина: детальность и качество разбора
    - Актуальность: релевантность для текущего времени
    
    ЦЕЛЕВАЯ АУДИТОРИЯ (выбери 1-2 наиболее подходящих):
    - Начинающие предприниматели
    - Опытные бизнесмены
    - Маркетологи
    - IT-специалисты
    - Фрилансеры
    - Инвесторы
    - Студенты
    
    ВРЕМЯ НА ИЗУЧЕНИЕ:
    - Быстро (5-10 мин)
    - Средне (15-30 мин)
    - Долго (1+ час)
    
    КАТЕГОРИЯ:
    - Стратегия
    - Маркетинг
    - Продажи
    - Финансы
    - Технологии
    - Личная эффективность
    - Аналитика
    
    УРОВЕНЬ СЛОЖНОСТИ:
    - Простой (можно внедрить за день)
    - Средний (требует недели планирования)
    - Сложный (нужна серьезная подготовка)
    
    ROI ПОТЕНЦИАЛ:
    - Высокий (быстрая окупаемость)
    - Средний (долгосрочная выгода)
    - Низкий (больше для развития)
    
    СТАДИЯ БИЗНЕСА:
    - Стартап (0-2 года)
    - Рост (2-5 лет)
    - Зрелый бизнес (5+ лет)
    
    ВРЕМЕННЫЕ РАМКИ РЕЗУЛЬТАТА:
    - Быстро (1-4 недели)
    - Средне (1-3 месяца)
    - Долго (3+ месяцев)
    
    Ответь ТОЛЬКО в формате JSON:
    {{
        "title": "Краткий заголовок (до 110 символов)",
        "summary": "В этом обзоре ты узнаешь об [основная тема], и вот наша оценка данного поста: [краткая оценка]. Идеи как использовать это каждый день: [2-3 практические идеи]",
        "overall_score": [общая оценка 1-10],
        "scores": {{
            "practicality": [1-10],
            "novelty": [1-10],
            "depth": [1-10],
            "relevance": [1-10]
        }},
        "target_audience": ["аудитория1", "аудитория2"],
        "reading_time": "время",
        "category": "категория",
        "complexity_level": "уровень сложности",
        "roi_potential": "ROI потенциал",
        "business_stage": "стадия бизнеса",
        "result_timeframe": "временные рамки",
        "action_checklist": ["действие 1", "действие 2", "действие 3"],
        "main_risks": ["риск 1", "риск 2"],
        "score_reason": "Объяснение общей оценки (1-2 предложения)",
        "content_quality": "{article.get('content_source', 'unknown')}"
    }}
    
    Требования:
    - Ответ на русском языке
    - Формат summary должен строго следовать шаблону "В этом обзоре ты узнаешь об..."
    - Общая оценка = среднее арифметическое 4 параметров
    - action_checklist должен содержать 3-5 конкретных действий
    - main_risks должен содержать 1-3 основных риска
    - Будь объективным в оценках
    """
    
    # Prepare OpenAI API request
    url = "https://api.openai.com/v1/chat/completions"
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system", 
                "content": "Ты эксперт-аналитик бизнес-контента с многолетним опытом в стратегическом планировании и оценке рисков. Ты умеешь объективно оценивать материалы по множественным критериям, определять целевую аудиторию и создавать практические планы действий. Твоя задача - создавать максимально детальные аналитические обзоры с конкретными рекомендациями."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
        "response_format": {"type": "json_object"}
    }
    
    try:
        # Make the API request
        req = urllib.request.Request(url, 
                                   data=json.dumps(data).encode('utf-8'),
                                   headers={
                                       'Content-Type': 'application/json',
                                       'Authorization': f'Bearer {openai_api_key}'
                                   })
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            # Extract the response
            content = result['choices'][0]['message']['content']
            analysis_data = json.loads(content)
            
            # Validate and clean data
            validated_analysis = validate_enhanced_analysis(analysis_data, article)
            
            logger.info(f"✅ Enhanced analysis generated! Overall Score: {validated_analysis['overall_score']}/10")
            return validated_analysis
            
    except Exception as e:
        logger.error(f"❌ Error generating enhanced analysis: {e}")
        return create_fallback_analysis(article)


def validate_enhanced_analysis(data, article):
    """Validate and clean enhanced analysis data."""
    # Validate overall score
    overall_score = data.get('overall_score', 7)
    if not isinstance(overall_score, (int, float)) or overall_score < 1 or overall_score > 10:
        overall_score = 7
    
    # Validate scores
    scores = data.get('scores', {})
    for key in ['practicality', 'novelty', 'depth', 'relevance']:
        if key not in scores or not isinstance(scores[key], (int, float)) or scores[key] < 1 or scores[key] > 10:
            scores[key] = 7
    
    # Recalculate overall score as average
    calculated_overall = round(sum(scores.values()) / len(scores))
    
    # Validate other fields
    validated_data = {
        'title': data.get('title', article['title'])[:110],
        'summary': data.get('summary', 'Краткий обзор статьи'),
        'overall_score': calculated_overall,
        'scores': scores,
        'target_audience': data.get('target_audience', ['начинающие предприниматели']),
        'reading_time': data.get('reading_time', 'средне (15-30 мин)'),
        'category': data.get('category', 'стратегия'),
        'complexity_level': data.get('complexity_level', 'средний'),
        'roi_potential': data.get('roi_potential', 'средний'),
        'business_stage': data.get('business_stage', 'рост (2-5 лет)'),
        'result_timeframe': data.get('result_timeframe', 'средне (1-3 месяца)'),
        'action_checklist': data.get('action_checklist', ['Изучить материал', 'Составить план', 'Начать внедрение']),
        'main_risks': data.get('main_risks', ['Недостаток ресурсов', 'Сложность внедрения']),
        'score_reason': data.get('score_reason', 'Полезный материал с практическими рекомендациями'),
        'content_quality': data.get('content_quality', article.get('content_source', 'unknown'))
    }
    
    return validated_data


def create_fallback_analysis(article):
    """Create fallback analysis when AI fails."""
    return {
        'title': article['title'][:110],
        'summary': 'В этом обзоре ты узнаешь об интересных бизнес-идеях, и вот наша оценка данного поста: полезный материал для изучения. Идеи как использовать это каждый день: изучи основные принципы, адаптируй под свою ситуацию, начни с малых шагов.',
        'overall_score': 7,
        'scores': {
            'practicality': 7,
            'novelty': 6,
            'depth': 7,
            'relevance': 7
        },
        'target_audience': ['начинающие предприниматели', 'опытные бизнесмены'],
        'reading_time': 'средне (15-30 мин)',
        'category': 'стратегия',
        'complexity_level': 'средний',
        'roi_potential': 'средний',
        'business_stage': 'рост (2-5 лет)',
        'result_timeframe': 'средне (1-3 месяца)',
        'action_checklist': ['Изучить материал детально', 'Выделить ключевые идеи', 'Составить план внедрения', 'Начать с пилотного проекта'],
        'main_risks': ['Недостаток опыта', 'Ограниченные ресурсы'],
        'score_reason': 'Стандартная оценка (ошибка анализа)',
        'content_quality': article.get('content_source', 'fallback')
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


def send_telegram_message(article, analysis):
    """Send enhanced message to Telegram."""
    logger.info("📱 Sending enhanced Telegram message...")
    
    telegram_token = os.environ.get('TELEGRAM_TOKEN')
    telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not telegram_token or not telegram_chat_id:
        logger.error("❌ Telegram credentials not found")
        return False
    
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
    
    # Send message
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        
        data = {
            'chat_id': telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False
        }
        
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=encoded_data)
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('ok'):
                logger.info("✅ Telegram message sent successfully!")
                return True
            else:
                logger.error(f"❌ Telegram API error: {result}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error sending Telegram message: {e}")
        return False


def main():
    """Main function."""
    logger.info("🚀 Starting FastFounder Daily Bot (Authenticated Version)")
    
    # Initialize authenticated scraper
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
    
    # Get RSS feed
    articles = get_rss_feed()
    
    if not articles:
        logger.error("❌ No articles found in RSS feed")
        return
    
    # Process the latest article
    article = articles[0]
    logger.info(f"📰 Processing article: {article['title']}")
    
    # Scrape article content (authenticated or fallback)
    article_data = scrape_article_content_authenticated(article, scraper)
    
    # Generate enhanced analysis
    analysis = generate_enhanced_analysis(article_data)
    
    # Send to Telegram
    success = send_telegram_message(article_data, analysis)
    
    if success:
        logger.info("🎉 Daily digest sent successfully!")
    else:
        logger.error("❌ Failed to send daily digest")


if __name__ == "__main__":
    main() 