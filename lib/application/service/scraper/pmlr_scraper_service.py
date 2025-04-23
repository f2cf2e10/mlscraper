from datetime import datetime
from logging import Logger
import re
from bs4 import BeautifulSoup
import requests
from typing import List, Dict

from lib.application.dto.model import PaperCreateDto, PaperDto
from lib.application.ports.inbound.paper_scraper_usecase import PaperScraperUseCase


class PmlrScraper(PaperScraperUseCase):
    BASE_URL = "https://proceedings.mlr.press"
    conference = "PMLR"

    def __init__(self, volume: int):
        self.volume = volume

    def extract_links(self, logger: Logger) -> List[str]:
        index_url = f'{self.BASE_URL}/{self.volume}'
        logger.info(f"Fetching paper list from {index_url}")

        response = requests.get(index_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        paper_links = []
        h2_tag = soup.find('h2')
        if h2_tag:
            match = re.search(r':\s*(.*?),', h2_tag.get_text())
            if match:
                self.conference += f" - {match.group(1).strip()}"
            match_date = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', h2_tag.get_text())
            if match_date:
                day = int(match_date.group(1))
                month_name = match_date.group(2)
                year = int(match_date.group(3))
                month_number = datetime.strptime(month_name, '%B').month
                self.date = datetime(year, month_number, day)

        for link in soup.find_all('a', href=True):
            href = link['href']

            if 'proceedings' in href.lower() or 'paper' in href.lower():
                if not href.startswith('http'):
                    href = 'https://proceedings.mlr.press' + href
                if href.endswith('html'):
                    paper_links.append(href)

        return paper_links

    def process_link(self, link: str, logger: Logger) -> PaperCreateDto:
        logger.info(f"Fetching {link}")
        response = requests.get(link)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else 'No title'

        authors_tag = soup.find('span', class_='authors')
        authors = authors_tag.get_text(
            strip=True).split(",") if authors_tag else [] 

        abstract_tag = soup.find('div', class_='abstract')
        abstract = abstract_tag.get_text(
            strip=True) if abstract_tag else None

        pdf = None
        for link in soup.find_all('a', href=True):
            if link['href'].lower().endswith('pdf'):
                pdf = link['href']
                if not pdf.startswith('http'):
                    pdf = 'https://proceedings.mlr.press' + pdf
                break

        return PaperCreateDto(title=title,
                              authors=authors,
                              abstract=abstract,
                              publication_date=self.date,
                              volume=self.volume,
                              keywords='',
                              url=pdf,
                              conference=self.conference)
