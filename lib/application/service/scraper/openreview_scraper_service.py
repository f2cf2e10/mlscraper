from datetime import datetime
from logging import Logger
import openreview
from typing import List
from lib.application.dto.model import PaperCreateDto
from lib.application.ports.inbound.paper_scraper_usecase import PaperScraperUseCase


class OpenReviewScraper(PaperScraperUseCase):
    BASE_URL = "https://api2.openreview.net"

    def __init__(self, volume: str, uname: str, pwd: str):
        self.client = openreview.api.OpenReviewClient(
            baseurl=self.BASE_URL,
            username=uname,
            password=pwd)
        self.volume = volume
        self.group_id = f"ICLR.cc/{volume}/Conference"

    def extract_links(self, logger: Logger) -> List[openreview.Note]:
        logger.info(f"Fetching paper list from {self.group_id}")
        submissions = self.client.get_all_notes(
            content={'venueid': self.group_id})
        return submissions

    def process_link(self, note: openreview.Note, logger: Logger) -> PaperCreateDto:
        logger.info(f"Processing Openreview note {note.id}.")
        paper = PaperCreateDto(title=note.content['title']['value'],
                               authors=note.content['authors']['value'],
                               abstract=note.content['abstract']['value'],
                               conference="ICLR",
                               volume=self.volume,
                               url=f"https://openreview.net{note.content['pdf']['value']}",
                               keywords="|".join(
                                   note.content["keywords"]['value']),
                               publication_date=datetime.fromtimestamp(note.tmdate/1000))
        return paper
