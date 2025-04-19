from datetime import datetime
from bs4 import BeautifulSoup
import requests
from typing import List, Dict

from lib.application.dto.model import PaperDto
from lib.application.ports.inbound.paper_scraper_usecase import PaperScraperUseCase


class PmlrScraper(PaperScraperUseCase):

    BASE_URL = "https://proceedings.mlr.press"

    def __init__(self, year: int):
        self.year = year
        self.volumes = self._get_volumes_for_year()

    def _get_volumes_for_year(self) -> List[str]:
        resp = requests.get(self.BASE_URL)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        volumes = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('v') and href.endswith('/'):
                volume_url = f"{self.BASE_URL}/{href}"
                volume_year = self._extract_year_from_volume(volume_url)
                if volume_year == self.year:
                    volumes.append(volume_url)
        return volumes

    def _extract_year_from_volume(self, volume_url: str) -> int:
        resp = requests.get(volume_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        year_tag = soup.find(
            'meta', attrs={"name": "citation_publication_date"})
        if year_tag and "content" in year_tag.attrs:
            date_str = year_tag["content"]
            year = int(date_str.split("-")[0])
            return year
        return -1

    def list_papers(self) -> List[PaperDto]:
        papers = []
        for volume_url in self.volumes:
            paper = self._scrape_volume(volume_url)
            papers.extend(paper)
        return papers

    def _scrape_volume(self, volume_url: str) -> List[PaperDto]:
        resp = requests.get(volume_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find the conference name
        conf_tag = soup.find('h1')
        conference = conf_tag.get_text(
            strip=True) if conf_tag else "Unknown Conference"

        papers = []
        for div in soup.find_all("div", class_="paper"):
            title_tag = div.find("p", class_="title")
            authors_tag = div.find("p", class_="authors")
            abstract_tag = div.find("div", class_="abstract")
            pdf_link = div.find("a", text="Download PDF")

            title = title_tag.get_text(strip=True) if title_tag else ""
            authors = [a.strip() for a in authors_tag.get_text(
                strip=True).split(",")] if authors_tag else []
            abstract = abstract_tag.get_text(
                strip=True) if abstract_tag else ""
            pdf_url = self.BASE_URL + pdf_link['href'] if pdf_link else ""
            paper_url = volume_url  # optional improvement later

            keywords, publication_date = self._scrape_paper_page(
                paper_url) if paper_url else ([], "")
            papers.append(PaperDto(
                title=title,
                authors=authors,
                abstract=abstract,
                conference=conference,
                url=pdf_url,
                keywords=keywords,
                publication_date=publication_date
            ))

        return papers

    def _scrape_paper_page(self, paper_url: str) -> tuple[List[str], str]:
        if not paper_url:
            return [], ""

        resp = requests.get(paper_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find keywords
        keywords_meta = soup.find_all(
            'meta', attrs={"name": "citation_keywords"})
        keywords = [meta['content']
                    for meta in keywords_meta] if keywords_meta else []

        # Find publication date
        pub_date_meta = soup.find(
            'meta', attrs={"name": "citation_publication_date"})
        publication_date = pub_date_meta['content'] if pub_date_meta else ""

        return keywords, publication_date
