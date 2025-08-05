"""Конфигурация для работы с внешними источниками книг"""

import os
from django.conf import settings

# Настройки Tor (SOCKS5 прокси для onion-адресов через Tor Browser)
TOR_PROXY_CONFIG = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

# Настройки Флибусты (onion-адрес через Tor)
FLIBUSTA_CONFIG = {
    'onion_url': 'http://flibustaongezhld6dibs2dps6vm4nvqg2kp7vgowbu76tzopgnhazqd.onion',
    'api_endpoints': {
        'search': '/booksearch',
        'download': '/b/{book_id}/download',
        'info': '/b/{book_id}'
    },
    'supported_formats': ['fb2', 'epub', 'mobi', 'txt', 'pdf'],
    'timeout': 30,
    'max_retries': 3
}

# LibGen удален - используем только Флибусту

# Общие настройки
EXTERNAL_SOURCES_CONFIG = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'default_timeout': 30,
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'allowed_extensions': ['.fb2', '.epub', '.mobi', '.txt', '.pdf', '.djvu', '.zip'],
    'encoding_detection': True,
    'cache_duration': 3600  # 1 час
}

# Настройки безопасности
SECURITY_CONFIG = {
    'verify_ssl': True,
    'allow_redirects': True,
    'max_redirects': 5,
    'rate_limit': {
        'requests_per_minute': 30,
        'requests_per_hour': 500
    }
}

# Функция для получения настроек из переменных окружения
def get_config_value(key, default=None, config_type=str):
    """Получить значение конфигурации из переменных окружения или использовать значение по умолчанию"""
    env_key = f'EXTERNAL_BOOKS_{key.upper()}'
    value = os.getenv(env_key, default)
    
    if config_type == bool:
        return str(value).lower() in ('true', '1', 'yes', 'on')
    elif config_type == int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    elif config_type == list:
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return value or []
    
    return value

# Применение настроек из переменных окружения
if hasattr(settings, 'EXTERNAL_BOOKS_CONFIG'):
    # Обновляем конфигурацию значениями из Django settings
    user_config = getattr(settings, 'EXTERNAL_BOOKS_CONFIG', {})
    
    # Настройки прокси отключены
    # if 'tor_proxy' in user_config:
    #     TOR_PROXY_CONFIG.update(user_config['tor_proxy'])
    
    if 'flibusta' in user_config:
        FLIBUSTA_CONFIG.update(user_config['flibusta'])
    
    # LibGen удален - используем только Флибусту
    
    if 'general' in user_config:
        EXTERNAL_SOURCES_CONFIG.update(user_config['general'])
    
    if 'security' in user_config:
        SECURITY_CONFIG.update(user_config['security'])