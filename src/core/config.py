from sys import stdout
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any

from loguru import logger

import yaml

BASE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)

@dataclass
class Config:
    """Config - Конфигуарационный класс для хранение статистических данных"""
    debug: bool = False
    save_file: str = "data.json"
    log_level: str = "INFO"
    log_file: Path = "logs.log"
    
    max_worker: int = 5
    headless: bool = False
    delay: float = 1_800
    timeout: float = 60 * 1000
    
    def __post_init__(self):
        try:
            with open('config.yaml', 'r') as file:
                config: Dict[str, Any] = yaml.safe_load(file)
        except OSError:
            config = {}
            
        try:
            self.debug = bool(config.get('debug', False))
            self.save_file = config.get('save_file', "data.json")
            
            log_box = config.get("log", {})
            self.log_level = log_box.get("log_level", "INFO")
            self.log_file = Path(log_box.get("log_file", "logs.log"))
            
            self.max_worker = int(config.get("max_worker", 5))
            self.headless = bool(config.get("headless", False))
            self.delay = int(config.get("delay", 1_800))
            self.timeout = float(config.get("timeout", 60)) * 1000
            
        except Exception as e:
            logger.error(f"Аргумент не правильный (error={e})")
        
config = Config()
logger.remove()

if not config.debug:
    logger.add(stdout, format=BASE_FORMAT, level=config.log_level)
    logger.add(config.log_file, format=BASE_FORMAT, level=config.log_level)
else:
    logger.add(stdout, level="DEBUG")
    logger.add(config.log_file, level="DEBUG")