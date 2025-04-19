import requests
from typing import List
from bs4 import BeautifulSoup
from datetime import datetime
from logging import Logger
from lib.application.dto.model import PaperCreateDto
from lib.application.ports.inbound.paper_scraper_usecase import PaperScraperUseCase


class NeurIpsScraper(PaperScraperUseCase):
    BASE_URL = "https://proceedings.neurips.cc"

    def __init__(self, year: str):
        self.year = year

    def extract_links(self, logger: Logger) -> List[str]:
        index_url = f"{self.BASE_URL}/paper/{self.year}"

        logger.info(f"Fetching paper list from {index_url}")
        resp = requests.get(index_url)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        paper_list = soup.find(class_='paper-list')
        paper_links = paper_list.find_all('li')
        links = []
        for li in paper_links:
            paper_info = li.find('a')
            if not paper_info:
                continue

            paper_relative_url = paper_info['href']
            links.append(f"{self.BASE_URL}{paper_relative_url}")
        return links

    def process_link(self, link: str, logger: Logger) -> PaperCreateDto:
        logger.info(f"Fetching {link}")
        resp = requests.get(link)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Extract title
        title_tag = soup.find('h4')
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Extract authors
        authors_tag = soup.find('h4', string="Authors")
        authors = []
        if authors_tag:
            authors_p = authors_tag.find_next_sibling('p')
            if authors_p:
                authors_text = authors_p.get_text(strip=True)
                authors = [author.strip()
                           for author in authors_text.split(',')]

        # Extract abstract
        abstract_tag = soup.find('h4', string="Abstract")
        abstract = ""
        if abstract_tag:
            abstract_p = abstract_tag.find_next_sibling('p')
            if abstract_p:
                abstract = abstract_p.get_text(strip=True)

        pdf_url = ""
        paper_buttons = soup.find_all('a', class_="btn", href=True)
        for btn in paper_buttons:
            if "Paper" in btn.get_text():
                pdf_url = btn['href']
                if not pdf_url.startswith("http"):
                    pdf_url = f"https://proceedings.neurips.cc{pdf_url}"
                break

        return PaperCreateDto(title=title,
                              authors=authors,
                              abstract=abstract,
                              publication_date=datetime.fromisoformat(
                                  f"{self.year}-12-01"),
                              url=pdf_url,
                              conference="NeurIPS",
                              keywords="")
