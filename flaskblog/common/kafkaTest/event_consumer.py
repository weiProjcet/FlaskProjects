"""
用户行为事件消费者服务
"""
import json
import logging
from kafka import KafkaConsumer
from .kafka_config import KafkaConfig


class UserBehaviorConsumer:
    def __init__(self):
        """
        初始化Kafka消费者用于处理用户行为数据
        """
        self.consumer = KafkaConsumer(
            KafkaConfig.USER_BEHAVIOR_TOPIC,
            **KafkaConfig.CONSUMER_CONFIG
        )

        # 配置日志
        self.logger = logging.getLogger(__name__)

    def start_consuming(self):
        """
        开始消费用户行为事件
        """
        self.logger.info("开始监听用户行为事件...")
        for message in self.consumer:
            try:
                event_data = message.value
                self.handle_event(event_data, message.key)
            except Exception as e:
                self.logger.error(f"处理事件时出错: {e}")

    def handle_event(self, event_data, user_id):
        """
        处理单个用户行为事件
        """
        event_type = event_data.get('event_type')
        timestamp = event_data.get('timestamp')

        self.logger.info(f"处理事件: {event_type} 用户: {user_id} 时间: {timestamp}")

        # 根据事件类型进行不同处理
        handlers = {
            'page_view': self.handle_page_view,
            'click': self.handle_click,
            'form_submit': self.handle_form_submit
        }

        handler = handlers.get(event_type, self.handle_generic_event)
        handler(event_data)

    def handle_page_view(self, event_data):
        """处理页面浏览事件"""
        user_id = event_data.get('user_id')
        page_url = event_data.get('page_url')
        referrer = event_data.get('additional_data', {}).get('referrer')

        # 这里可以实现具体的业务逻辑
        print(f"[页面浏览] 用户 {user_id} 访问 {page_url}, 来源: {referrer}")

    def handle_click(self, event_data):
        """处理点击事件"""
        user_id = event_data.get('user_id')
        page_url = event_data.get('page_url')
        element_id = event_data.get('element_id')

        print(f"[点击事件] 用户 {user_id} 在 {page_url} 点击了 {element_id}")

    def handle_form_submit(self, event_data):
        """处理表单提交事件"""
        user_id = event_data.get('user_id')
        page_url = event_data.get('page_url')

        print(f"[表单提交] 用户 {user_id} 在 {page_url} 提交表单")

    def handle_generic_event(self, event_data):
        """处理通用事件"""
        print(f"[通用事件] {event_data}")

    def close(self):
        """关闭消费者连接"""
        self.consumer.close()
