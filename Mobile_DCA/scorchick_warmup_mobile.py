import os
import time
import threading
import psutil  # Make sure psutil is installed in Termux or environment

# === Configuration ===
MODEL_PATHS = [
    os.path.expanduser("~/EdenOS_Mobile/eden_models/Fast_Qwen2.5-1.5B-Instruct.gguf"),
    os.path.expanduser("~/EdenOS_Mobile/eden_models/Qwen3-8B.gguf"),
    os.path.expanduser("~/EdenOS_Mobile/eden_models/Llama-2-7b-chat-ms.gguf"),
    os.path.expanduser("~/EdenOS_Mobile/eden_models/SmoLLM2-360M-Instruct.gguf")
]
TOUCH_INTERVAL = 300  # seconds between touching model files
RAM_THRESHOLD_MB = 300  # If free RAM below this, consider unload

class ScorchickWarmupDaemon:
    def __init__(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True

    def _touch_models(self):
        now = time.time()
        for path in MODEL_PATHS:
            try:
                os.utime(path)
                print(f"⚡ Touched model file: {path}")
            except Exception as e:
                print(f"⚠️ Failed to touch {path}: {e}")

    def _check_memory(self):
        mem = psutil.virtual_memory()
        free_mb = mem.available / (1024 * 1024)
        print(f"🧠 Free RAM: {free_mb:.1f} MB")
        if free_mb < RAM_THRESHOLD_MB:
            print("⚠️ Low RAM detected - consider unloading models")

    def _run(self):
        while self.running:
            self._touch_models()
            self._check_memory()
            time.sleep(TOUCH_INTERVAL)

    def start(self):
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

def main():
    daemon = ScorchickWarmupDaemon()
    print("Scorchick Warmup Daemon started.")
    daemon.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping Scorchick Warmup Daemon...")
        daemon.stop()

if __name__ == "__main__":
    main()
