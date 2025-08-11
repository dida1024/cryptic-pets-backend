import logging
import sys

from loguru import logger

from infrastructure.config import settings  # 從您的設定檔中導入設定


def setup_logging():
    """
    設定 Loguru，使其同時滿足開發和生產環境的需求。
    """
    # 移除 Loguru 預設的 handler，以便完全自訂
    logger.remove()

    # 開發環境日誌格式：帶有顏色和詳細資訊，輸出到控制台
    dev_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # 生產環境日誌格式：JSON 格式，便於日誌系統收集
    # `serialize=True` 會將日誌記錄轉換為 JSON 字串
    prod_format = "{message}"

    # 根據環境變數來決定使用哪種格式
    if settings.ENVIRONMENT == "development":
        # 開發環境：輸出到標準錯誤流 (stderr)
        logger.add(
            sys.stderr,
            level=settings.LOG_LEVEL.upper(),
            format=dev_format,
            colorize=True # 開啟顏色
        )
    else:
        # 生產環境：輸出 JSON 到標準輸出流 (stdout)
        logger.add(
            sys.stdout,
            level=settings.LOG_LEVEL.upper(),
            format=prod_format,
            serialize=True # ⭐ 核心：序列化為 JSON
        )

    # ⭐ 關鍵一步：攔截所有來自標準庫 logging 模組的日誌
    #     這將確保 uvicorn, fastapi, sqlalchemy 等庫的日誌也會被 Loguru 捕獲並重新格式化
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # 取得對應的 loguru 層級
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # 從記錄中找到對應的 logger
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.info("日誌系統設定完成。")
