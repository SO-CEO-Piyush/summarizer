import bs4
import logging

logger = logging.getLogger(__name__)

class Parser:
    def parse(self, html: str) -> str:
        logger.info(f"parsing html of length {len(html)}")
        soup = bs4.BeautifulSoup(html, "html.parser")
        text = soup.get_text(strip=True, separator=' ')
        logger.info(f"extracted {len(text)} characters of text")
        return text
