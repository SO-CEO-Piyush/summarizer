import subprocess
import logging

logger = logging.getLogger(__name__)

def scrape(url: str) -> str:
    logger.info(f"scraping url: {url}")
    result = subprocess.run(
        ["spider", "--url", url, "--budget", "*,1", "scrape", "--output-html"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        logger.error(f"scraping failed with code {result.returncode}: {result.stderr}")
    else:
        logger.info(f"scraped {len(result.stdout)} characters")
    return result.stdout
