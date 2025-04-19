from io import BytesIO
from typing import IO
from minio import Minio
from minio.error import S3Error

from lib.application.ports.outbound.paper_storage import PaperStorage


class MinioPaperStorage(PaperStorage):
    def __init__(self, client: Minio, bucket_name: str):
        self.client = client
        self.bucket_name = bucket_name

    def upload_file(self, key: str, content: IO[bytes]) -> bool:
        try:
            pdf = content.read()
            if pdf.startswith(b'%PDF'):
                result = self.client.put_object(
                    self.bucket_name,
                    f'{key}.pdf',
                    BytesIO(pdf),
                    len(pdf),
                    content_type="application/pdf"
                )
                return True
            else: 
                return False
        except S3Error as e:
            print(f"Error uploading file: {e}")
            raise e

    def get_file(self, key: str) -> IO[bytes]:
        try:
            file_data = self.client.get_object(self.bucket_name, key)
            return file_data.data
        except S3Error as e:
            print(f"Error retrieving file: {e}")
            raise e
