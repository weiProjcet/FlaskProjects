import threading
from common.kafkaTest.behavior_log_consumers import create_login_consumer, create_view_consumer, \
    create_download_consumer


def run_consumer(consumer_factory, name):
    """运行单个消费者"""
    consumer = consumer_factory()
    print(f"Starting {name} consumer...")
    consumer.start_consuming()


if __name__ == "__main__":
    # 创建并启动各个消费者线程
    consumers = [
        (create_login_consumer, "Login"),
        (create_view_consumer, "View"),
        (create_download_consumer, "Download")
    ]

    threads = []
    for consumer_factory, name in consumers:
        thread = threading.Thread(target=run_consumer, args=(consumer_factory, name))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    # 保持主线程运行
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Stopping all consumers...")
