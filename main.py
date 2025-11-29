import asyncio
import json

from playwright.async_api import async_playwright
from loguru import logger

from src.manager.live_manager import LiveManager
from src.core import config

async def main():
    async with async_playwright() as p:
        browser = None
        try:
            while True:
                result = {}
                
                browser = await p.chromium.launch()
                manager = LiveManager(browser)
                
                today_matches = await manager.get_today_matches()
                if not today_matches:
                    logger.warning("Не удалось получить данные, повтор операции")
                    continue
                    
                tasks = [manager.get_info(match) for match in today_matches]
                
                for task in asyncio.as_completed(tasks):
                    response = await task
                    result[response.id] = response.to_dict()
                
                with open(config.save_file, 'w', encoding='utf-8') as file:
                    json.dump(result, file)
                logger.success(f"Данные обновлены (path={config.save_file})")
                    
                logger.info(f"Ожидание {config.delay} секунд")
                await asyncio.sleep(config.delay)
            
        except asyncio.CancelledError:
            logger.info("Процесс остановлен пользователем")
            
        except Exception as e:
            logger.critical(f"Неизвестная ошибка (error={e})")
            
        finally:
            if browser:
                try:
                    await browser.close()
                    await p.stop()
                except Exception:
                    logger.warning("Не удалось безопасно закрыть браузер (Можно игнорировать)")

if __name__ == "__main__":
    try:
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("Процесс остановлен пользователем")
        
    except Exception as e:
        logger.critical(f"Неизвестная ошибка (error={e})")
        
    finally:
        logger.info("Программа приостоновила свою работу")