import logging
import sys
from pathlib import Path

# Создаем директорию для логов, если она не существует
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Настройка логгеров для разных модулей
loggers = {
    'api': logging.getLogger('api'),
    'core': logging.getLogger('core'),
    'models': logging.getLogger('models'),
    'services': logging.getLogger('services')
}

# Устанавливаем уровень логирования для разных модулей
for logger in loggers.values():
    logger.setLevel(logging.INFO) 