from prometheus_client  import Gauge, Counter, Summary, Histogram


class Prom:
    SEND_GMAIL_NOTIFICATION = Summary('send_gmail_notification_latency_seconds', 'Time spent processing send gmail notification')
