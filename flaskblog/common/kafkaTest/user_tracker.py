"""
用户行为跟踪器
"""

import json
import uuid
from datetime import datetime
from kafka import KafkaProducer
from .kafka_config import KafkaConfig


class UserBehaviorTracker:
    def __init__(self):
        """
        初始化Kafka生产者用于用户行为跟踪
        """
        self.producer = KafkaProducer(**KafkaConfig.PRODUCER_CONFIG)
        self.topic = KafkaConfig.USER_BEHAVIOR_TOPIC

    def track_event(self, user_id, event_type, page_url=None, element_id=None,
                    additional_data=None):
        """
        跟踪用户行为事件

        Args:
            user_id: 用户ID
            event_type: 事件类型
            page_url: 页面URL
            element_id: 元素ID
            additional_data: 额外数据
        """
        event_data = {
            'event_id': str(uuid.uuid4()),
            'user_id': user_id,
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'page_url': page_url,
            'element_id': element_id,
            'additional_data': additional_data or {}
        }

        # 发送事件到Kafka
        future = self.producer.send(
            self.topic,
            key=user_id,
            value=event_data
        )

        # 异步处理发送结果
        future.add_callback(self._on_send_success)
        future.add_errback(self._on_send_error)

    def _on_send_success(self, record_metadata):
        """发送成功回调"""
        print(f"Event sent to partition {record_metadata.partition}")

    def _on_send_error(self, exc):
        """发送失败回调"""
        print(f"Failed to send event: {exc}")

    def track_page_view(self, user_id, page_url, referrer=None):
        """跟踪页面浏览事件"""
        self.track_event(
            user_id=user_id,
            event_type='page_view',
            page_url=page_url,
            additional_data={'referrer': referrer}
        )

    def track_click(self, user_id, page_url, element_id):
        """跟踪点击事件"""
        self.track_event(
            user_id=user_id,
            event_type='click',
            page_url=page_url,
            element_id=element_id
        )

    def track_form_submit(self, user_id, page_url, form_data):
        """跟踪表单提交事件"""
        self.track_event(
            user_id=user_id,
            event_type='form_submit',
            page_url=page_url,
            additional_data={'form_data': form_data}
        )

    def close(self):
        """关闭生产者连接"""
        self.producer.close()


# 全局实例
tracker = UserBehaviorTracker()
