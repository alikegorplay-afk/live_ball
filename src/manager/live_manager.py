import asyncio
from urllib.parse import urljoin
from datetime import date

from playwright.async_api import Browser, Page
from playwright.async_api import TimeoutError
from playwright._impl._errors import TargetClosedError
from loguru import logger

from ..core import config
from ..core import LiveMatchResponse, ParseResult, MatchBlock
from ..tools import clean_text

class LiveManager:
    BASE_URL = "https://liveball.sx"
    MATCH_URL = urljoin(BASE_URL, "matches/{:02d}-{:02d}-{:02d}")
    
    def __init__(self, browser: Browser, max_workers: int = config.max_worker):
        self.browser = browser
        self.workers = max_workers
        self.semaphore = asyncio.Semaphore(max_workers)
        
        logger.debug("Инцилизация *GetManager*")
    
    async def get_today_matches(self) -> ParseResult | None:
        """Получение списка сегодняшних матчей

        Returns:
            ParseResult: Матчи на сегодняшнее число
            
        Example:
            >>> response = await get_today_matches()
            >>> print(type(response).__name__)
            >>> # ParseResult
        """
        today = date.today()
        return await self.get_matches(today.year, today.month, today.day)
    
    async def get_matches(self, year: int, month: int, day: int) -> ParseResult | None:
        """Получение списка матчов по указанной дате

        Args:
            year (int): Год проведение матча
            month (int): Месяц проведение матча
            day (int): День проведение матча

        Returns:
            ParseResult: Матчи на указанное число
            
        Example:
            >>> response = await get_matches(2025, 11, 28)
            >>> print(type(response).__name__)
            >>> # ParseResult
        """
        async with self.semaphore:
            context = await self.browser.new_context()
            page = await context.new_page()
            
            url = self.MATCH_URL.format(year, month, day)
            try:
                if not await self._fetch_page(url, page):
                    return None
                
                return await self._parse_matches(page)
                
            except Exception as e:
                logger.error(f"Не удалось получить данные (error={e})")
                return None
                
            finally:
                await context.close()
    
    async def get_info(self, url: str | MatchBlock) -> LiveMatchResponse | None:
        """Получить информацию об матче

        Args:
            url (str | MatchBlock): URL к  матчу

        Raises:
            TypeError: Если указан неправильный тип данных

        Returns:
            LiveMatchResponse | None: LiveMatchResponse, если парсинг удачный иначе None
        """
        if isinstance(url, MatchBlock):
            url = url.url
        elif isinstance(url, str):
            url = url
        else:
            raise TypeError(f"Неподдерживаемый тип данных {type(url).__name__}")
        
        async with self.semaphore:
            context = await self.browser.new_context()
            page = await context.new_page()
            
            try:
                if not await self._fetch_page(url, page):
                    return None

                return await self._parse_match(page)
                
            except Exception as e:
                logger.error(f"Не удалось получить данные (error={e})")
                return None

            finally:
                await context.close()
                
    async def _parse_match(self, page: Page) -> LiveMatchResponse:
        """Парсинг матча

        Args:
            page (Page): экземпляр page

        Returns:
            LiveMatchResponse: Ифнормация об матче
        """
        title       =   await page.query_selector("div.info_match h2.counter_title")
        description =   await page.query_selector("div.info_match span.desc_stat")
        player      =   await page.query_selector("#player video")
        
        return LiveMatchResponse(
            url = page.url,
            title = clean_text(await title.text_content() or "") if title else None,
            description = clean_text(await description.text_content() or "") if description else None,
            m3u8_url = await player.get_attribute('src') if player else None
        )
        
    async def _parse_matches(self, page: Page) -> ParseResult:
        """Спарсить список матчей

        Args:
            page (Page): экземпляр page

        Returns:
            ParseResult: Список матчей
        """
        result = ParseResult()
        elements = await page.query_selector_all("div.live div.live_block2")
        for element in elements:
            url = await element.query_selector("a")
            left_team = await element.query_selector("div.left_team")
            right_team = await element.query_selector('div.right_team')
            
            result.urls.append(
                MatchBlock(
                    url = urljoin(self.BASE_URL, await url.get_attribute("href") or "404"),
                    left_team = (await left_team.text_content() or "unknown").strip(),
                    right_team = (await right_team.text_content() or "unknown").strip(),
                )
            )
        return result
        
    async def _fetch_page(self, url: str, page: Page):
        """Запрос к странице

        Args:
            url (str): URL к странице
            page (Page): экземпляр page

        Returns:
            bool (True | False): True если запрос успешный иначе False
        """
        try:
            logger.info(f"Попытка получить данные (url={url})")
            response = await page.goto(url)
            if not response or not response.ok:
                logger.warning(f"Не ожиданный код ответа (url={url}, status={response.status if response else "unknown"})")
                return False
            
            logger.info(f"Удалось получить данные (url={url}, status={response.status})")
            return True
        except TimeoutError as e:
            logger.error(f"Не удалось получить данные за указанное время (error={e})")
            logger.info("Рекемендуется использовать VPN/PROXY с европейским IP")
            return False
        
        except TargetClosedError:
            logger.warning("Браузер закрыт, невозможно получить данные")
            return False
        
        except Exception as e:
            logger.error(f"Не удалось получить данные (error={e})")
            return False