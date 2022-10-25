from esd_crawl.items import Table
from hashlib import md5
from io import BufferedReader, BytesIO
import logging
from pathlib import Path
import pdfplumber
import requests
from scrapy.pipelines.files import FSFilesStore
from scrapy.pipelines.media import MediaPipeline
import tempfile

# these libraries are quite noisy at their DEBUG log level, so override them
logging.getLogger("pdfminer").setLevel(logging.INFO)
logging.getLogger("PIL").setLevel(logging.INFO)


def pages_with_tables(path_or_fp: str | Path | BufferedReader):
    with pdfplumber.open(path_or_fp) as pdf:
        for page in pdf.pages:
            tables = page.find_tables()
            if len(tables) > 0:
                yield page


class TableFinder:
    def __init__(self, path="tables"):
        self.store = FSFilesStore(path)

    def persist_img(self, img, info: MediaPipeline.SpiderInfo, extension="png"):
        # based on
        # https://github.com/scrapy/scrapy/blob/e4f6545fe952f1c1e3324340ade4e19bfb8a197e/scrapy/pipelines/files.py#L500-L503
        buf = BytesIO()
        img.save(buf, extension)
        buf.seek(0)

        # https://stackoverflow.com/a/53732141/358804
        checksum = md5(img.tobytes()).hexdigest()
        path = f"{checksum}.{extension}"

        self.store.persist_file(path, buf, info)

        return path

    def save_table_img(self, page, info: MediaPipeline.SpiderInfo):
        img = page.to_image()
        finder = img.debug_tablefinder()
        # preview
        # finder.show()

        img = finder.annotated
        return self.persist_img(img, info)

    def find_table(self, page, info: MediaPipeline.SpiderInfo):
        img_path = self.save_table_img(page, info)
        return Table(page_num=page.page_number, img_path=img_path)

    def find_tables(
        self,
        pdf_path_or_fp: str | Path | BufferedReader,
        info: MediaPipeline.SpiderInfo,
    ):
        pages = pages_with_tables(pdf_path_or_fp)

        # not exactly sure what the info is used for, but passing it along to be consistent
        return [self.find_table(page, info) for page in pages]

    def find_tables_from_url(self, pdf_url: str, info: MediaPipeline.SpiderInfo):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as fp:
            response = requests.get(pdf_url)
            fp.write(response.content)
            fp.seek(0)

            return self.find_tables(fp, info)  # type: ignore
