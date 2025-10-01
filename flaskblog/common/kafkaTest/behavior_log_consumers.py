from kafka import KafkaConsumer
import json
import logging
import os
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BehaviorLogConsumer:
    def __init__(self, topic, group_id, log_file):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['192.168.10.8:9092', '192.168.10.8:9093', '192.168.10.8:9094'],
            group_id=group_id,
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        self.logger = logging.getLogger(group_id)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def start_consuming(self):
        """开始消费消息并记录到文件"""
        try:
            for message in self.consumer:
                event_data = message.value
                timestamp = datetime.fromtimestamp(event_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')

                if message.topic == 'user-login':
                    log_message = f"LOGIN - User: {event_data['user_id']}, IP: {event_data['ip_address']}, Time: {timestamp}"
                elif message.topic == 'blog-view':
                    log_message = f"VIEW - User: {event_data['user_id']}, Blog: {event_data['blog_id']}, Time: {timestamp}"
                elif message.topic == 'blog-download':
                    log_message = f"DOWNLOAD - User: {event_data['user_id']}, Blog: {event_data['blog_id']}, Size: {event_data['file_size']} bytes, Time: {timestamp}"
                else:
                    log_message = f"UNKNOWN - {json.dumps(event_data)}"

                self.logger.info(log_message)
                # 手动刷新日志缓冲区
                for handler in self.logger.handlers:
                    handler.flush()

        except KeyboardInterrupt:
            print(f"Consumer for {message.topic} interrupted")
        finally:
            self.consumer.close()


def create_logs(address):
    log_dir = os.path.join(os.getcwd(), 'logs')  # 创建logs目录
    os.makedirs(log_dir, exist_ok=True)  # 确保目录存在
    log_file = os.path.join(log_dir, str(address))
    return log_file


# 专门的消费者实例
def create_login_consumer():
    log_file = create_logs('login_events.log')
    return BehaviorLogConsumer('user-login', 'login-consumer-group', log_file)


def create_view_consumer():
    log_file = create_logs('view_events.log')
    return BehaviorLogConsumer('blog-view', 'view-consumer-group', log_file)


def create_download_consumer():
    log_file = create_logs('download_events.log')
    return BehaviorLogConsumer('blog-download', 'download-consumer-group', log_file)
