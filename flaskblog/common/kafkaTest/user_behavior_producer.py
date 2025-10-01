from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import time
from core import config


class UserBehaviorProducer:
    def __init__(self):
        """初始化 Kafka 生产者"""
        self.producer = None  # KafkaProducer 实例
        self.enabled = True  # 生产者启用状态标志
        kafka_enabled = getattr(config, 'KAFKA_ENABLED', True)
        # 如果Kafka被禁用，直接返回
        if not kafka_enabled:
            self.enabled = False
            return

        try:
            # 尝试创建 KafkaProducer 实例
            self.producer = KafkaProducer(
                bootstrap_servers=['192.168.10.8:9092', '192.168.10.8:9093', '192.168.10.8:9094'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=3  # 重试次数
            )
            print("Kafka producer initialized successfully.")
        except NoBrokersAvailable as e:
            print("Kafka brokers 不可用（服务端未启动或网络问题)")
            self.enabled = False
        except Exception as e:
            print(e)
            self.enabled = False

    def _safe_send(self, topic, value):
        """安全发送消息的方法"""
        if not self.enabled or self.producer is None:
            return

        try:
            self.producer.send(topic, value=value)
        except Exception as e:
            print(e)

    def send_login_event(self, user_id, ip_address, user_agent):
        """发送用户登录事件"""
        event = {
            'user_id': user_id,
            'timestamp': time.time(),
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        self._safe_send('user-login', event)

    def send_view_event(self, user_id, blog_id, session_id):
        """发送博客查看事件"""
        event = {
            'user_id': user_id,
            'blog_id': blog_id,
            'timestamp': time.time(),
            'session_id': session_id
        }
        self._safe_send('blog-view', event)

    def send_download_event(self, user_id, blog_id, file_size, download_type):
        """发送博客下载事件"""
        event = {
            'user_id': user_id,
            'blog_id': blog_id,
            'timestamp': time.time(),
            'file_size': file_size,
            'download_type': download_type
        }
        self._safe_send('blog-download', event)

    def close(self):
        """关闭生产者连接"""
        if self.producer:
            try:
                self.producer.close()
            except Exception as e:
                pass
