# Empire State Development data scraper

[![Tests](https://github.com/reinventalbany/esd-crawl/actions/workflows/test.yml/badge.svg)](https://github.com/reinventalbany/esd-crawl/actions/workflows/test.yml)

The goal of this tool is to find data on the [Empire State Development website](https://esd.ny.gov/), either in web pages or PDFs. [Running notes document.](https://docs.google.com/document/d/1HaWvHlpCYcD1SRmZn9DbsQoFCkvywBifcyME4cvjT-k/edit)

## Technical overview

The general steps of the workflow are:

1. Find PDFs throughout the site
1. Parse PDFs to find tables
1. Combine and de-duplicate the findings
1. Upload findings to Airtable for review

Technologies:

- The site-wide crawl is done via [Scrapy](https://scrapy.org/).
- The crawl of the [Reports page](https://esd.ny.gov/esd-media-center/reports?tid[0]=516) is done via [ParseHub](https://parsehub.com/), as that was easier to get working for the (AJAX) pagination.
- Table identification is done via [pdfplumber](https://github.com/jsvine/pdfplumber).
- Review of the identified tables is done via [Airtable](https://airtable.com/), as [an Interface](https://airtable.com/appdrqXSd2JNXkLp7/pag9j6GVdas1Xwayr?6bnb0=recaUXHnYswGGKKjI) could be built without .

## Usage

### Tables in PDFs

1. Crawl server-rendered pages

   1. Install dependencies
      - Python 3
      - [Poetry](https://python-poetry.org/)
      - [Visual debugging](https://github.com/jsvine/pdfplumber#visual-debugging)
   1. Clone repository
   1. From repository directory, run `poetry init`
   1. Run `poetry shell`
   1. Run the spider. This will take a few minutes.

      ```sh
      scrapy runspider esd_crawl/spiders/esd.py -L INFO -O results/scrapy.json
      ```

1. Crawl [Reports page](https://esd.ny.gov/esd-media-center/reports?tid[0]=516)

   1. Install [ParseHub](https://parsehub.com/)
   1. [Import](https://help.parsehub.com/hc/en-us/articles/115001733294-Export-Import-Projects) the Project, which is the `esd.ny.gov_Project.phj` file in this directory
   1. Run the Project
   1. Download Data as CSV
   1. Save as `results/parsehub.csv`
   1. Fetch and parse the PDFs:

      ```sh
      python scripts/parsehub.py
      ```

1. Combine the data from Scrapy and ParseHub

   ```sh
   python scripts/combine.py
   ```

1. Put table images somewhere publicly accessible. Example for [Google Cloud Storage](https://cloud.google.com/storage):
   1. [Create a bucket](https://cloud.google.com/storage/docs/creating-buckets)
   1. [Sync the `tables/` folder](#syncing-to-google-cloud-storage)
   1. [Make the bucket publicly readable](https://cloud.google.com/storage/docs/access-control/making-data-public#buckets)
   1. [Get the public URL](https://cloud.google.com/storage/docs/access-public-data#console) from one of the objects
1. Create the Airtable records

   1. [Get your Airtable API key](https://airtable.com/account)
   1. Set the key as an environment variable:

      ```sh
       export AIRTABLE_API_KEY=...
      ```

   1. Run the script. `IMG_PREFIX` will be the public object URL, minus the filename. Example:

      ```sh
      IMG_PREFIX=https://storage.googleapis.com/esd-data/tables/ python scripts/airtable.py
      ```

1. Triage records through [the Airtable interface](https://airtable.com/appdrqXSd2JNXkLp7/pag9j6GVdas1Xwayr) to be built without code.
1. Review ["kept" Tables](https://airtable.com/appdrqXSd2JNXkLp7/tblCqLOhNnkhJvc6z/viwWkwJ2Har1m6xA1?blocks=hide).

#### Syncing to Google Cloud Storage

Example, using [`gsutil`](https://cloud.google.com/storage/docs/gsutil):

```sh
gsutil -m rsync -r tables gs://esd-data/tables
```

## Broken links

```sh
scrapy runspider esd_crawl/spiders/broken.py -L INFO -O results/broken.csv
```

## Troubleshooting

### Limit the crawl

See the [close spider settings](https://docs.scrapy.org/en/latest/topics/extensions.html#module-scrapy.extensions.closespider). For example:

```sh
scrapy runspider esd_crawl/spiders/esd.py -s CLOSESPIDER_ITEMCOUNT=5
```

### Test a particular URL

```sh
scrapy parse --pipelines --spider <spider> <URL>

# or

python scripts/parse.py <PDF URL>
```

[More info on Scrapy's `parse`](https://docs.scrapy.org/en/latest/topics/commands.html#parse), and [general debugging info](https://docs.scrapy.org/en/latest/topics/debug.html).

### Notebook

There is also [a Jupyter notebook](esd_crawl/extract.ipynb) for experimentation.

## Tests

To run tests with [coverage](https://pytest-cov.readthedocs.io/):

```sh
make
```
