import psutil
import time
import threading


def Log_system_usage(logger, interval=5):
    process = psutil.Process()

    while True:
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            proc_mem = process.memory_info().rss / (1024 * 1024)
            threads = process.num_threads()

            logger.info(
                f"SYSTEM_USAGE | CPU: {cpu:.2f}% | MEM: {mem:.2f}% | "
                f"PROC_MEM: {proc_mem:.2f} MB | THREADS: {threads}"
            )

            time.sleep(interval)

        except Exception as e:
            logger.error(f"Error in system monitor: {e}", exc_info=True)