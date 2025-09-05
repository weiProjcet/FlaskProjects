import sys
import subprocess
import os
from app import app

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'start':
        # 启动完整服务的模式
        print("正在启动 Flask + Celery + Redis 服务...")

        try:
            # 启动 Celery Worker (在后台)
            print("启动 Celery Worker...")
            celery_process = subprocess.Popen([
                sys.executable, '-m', 'celery',
                '-A', 'celery_app.celery',
                'worker',
                '--loglevel=info',
                '--pool=solo'  # Windows 兼容的池类型
            ], cwd=os.getcwd(),
                creationflags=subprocess.CREATE_NEW_CONSOLE)  # 在新控制台窗口中运行

            print(f"Celery Worker PID: {celery_process.pid}")
            print("Celery Worker 已启动（在新控制台窗口中运行）")

            # 启动 Flask 应用
            print("启动 Flask 应用...")
            app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)

        except KeyboardInterrupt:
            print("\n正在关闭服务...")
            if 'celery_process' in locals():
                celery_process.terminate()
            print("服务已关闭")
        except Exception as e:
            print(f"启动过程中出现错误: {e}")
            if 'celery_process' in locals():
                celery_process.terminate()
    else:
        # 正常运行 Flask 应用（仅 Flask）
        print("启动 Flask 应用...")
        print("请确保 Redis 服务器已在后台运行...")
        print("如需同时启动 Celery，请使用: python run.py start")
        app.run(debug=True)
