"""
Kafka配置管理模块
"""


class KafkaConfig:
    # Kafka服务器地址
    BOOTSTRAP_SERVERS = ['localhost:9092']

    # 用户行为事件主题
    USER_BEHAVIOR_TOPIC = 'user_behavior_events'

    # 消费者组ID
    CONSUMER_GROUP_ID = 'flask_blog_analytics_group'

    # 生产者配置
    PRODUCER_CONFIG = {
        'bootstrap_servers': BOOTSTRAP_SERVERS,
        'value_serializer': lambda v: json.dumps(v).encode('utf-8'),
        'key_serializer': lambda k: k.encode('utf-8') if k else None
    }

    # 消费者配置
    CONSUMER_CONFIG = {
        'bootstrap_servers': BOOTSTRAP_SERVERS,
        'group_id': CONSUMER_GROUP_ID,
        'value_deserializer': lambda m: json.loads(m.decode('utf-8')),
        'key_deserializer': lambda k: k.decode('utf-8') if k else None,
        'auto_offset_reset': 'latest',
        'enable_auto_commit': True,
        'auto_commit_interval_ms': 1000
    }
