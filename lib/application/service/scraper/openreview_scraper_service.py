from datetime import datetime
from logging import Logger
import openreview
from typing import List
from lib.application.dto.model import PaperCreateDto
from lib.application.ports.inbound.paper_scraper_usecase import PaperScraperUseCase


class OpenReviewScraper(PaperScraperUseCase):
    BASE_URL_v2 = "https://api2.openreview.net"
    BASE_URL_v1 = "https://api.openreview.net"

    def __init__(self, volume: str, uname: str, pwd: str):
        self.client_v2 = openreview.api.OpenReviewClient(
            baseurl=self.BASE_URL_v2,
            username=uname,
            password=pwd)
        self.client_v1 = openreview.Client(
            baseurl=self.BASE_URL_v1,
            username=uname,
            password=pwd)
        self.volume = volume
        self.venue_id = f"ICLR.cc/{volume}"
        self.conference_id = f"ICLR.cc/{volume}/Conference"
        self.submission_id = f"ICLR.cc/{volume}/-/Submission"

    def extract_links(self, logger: Logger) -> List[openreview.Note]:
        api2_venue_group = self.client_v2.get_group(self.venue_id)
        use_v2 = api2_venue_group.domain is not None

        if use_v2:
            logger.info(f"Fetching paper list from {self.conference_id}")
            accepted_submissions = self.client_v2.get_all_notes(
                content={'venueid': self.venue_id})
            return accepted_submissions
        else:
            notes = self.client_v1.get_all_notes(
                invitation=self.submission_id, details='directReplies')
            notes = {note.id: note for note in notes}
            all_decision_notes = []
            for note_id, note in notes.items():
                all_decision_notes = all_decision_notes + \
                    [reply for reply in note.details["directReplies"]
                        if reply["invitation"].endswith("Decision")]

            accepted_submissions = []
            for decision_note in all_decision_notes:
                if 'Accept' in decision_note["content"]['decision']:
                    accepted_submissions.append(notes[decision_note['forum']])
        return accepted_submissions

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
