import os

# Flask settings
URL_PREFIX = os.getenv('URL_PREFIX', '/api/v1')
SERVICE_NAMESPACE = os.getenv('SERVICE_NAMESPACE', 'dev')
POD_NAME = os.getenv('POD_NAME', '')

# Logging
SERVICE_NAME = os.getenv('SERVICE_NAME', 'harp-notifications-gmail')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOKI_SERVER = os.getenv('LOKI_SERVER', '')
LOKI_PORT = os.getenv('LOKI_PORT', 3100)


class TracingConfig:
    TEMPO_URL = os.getenv('TEMPO_URL', '')


BOTS_SERVICE = os.getenv('BOTS_SERVICE', '')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))