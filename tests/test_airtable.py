from esd_crawl import airtable
import pytest
import responses
from responses.matchers import query_param_matcher


@pytest.fixture
def r_mock():
    # https://github.com/getsentry/responses#requestmock-methods-start-stop-reset
    mock = responses.RequestsMock(assert_all_requests_are_fired=True)
    mock.start()
    yield mock
    mock.stop()
    mock.reset()


def mock_create_record(r_mock, table_name):
    r_mock.post(
        airtable.table_api_url(table_name),
        json={"records": [{"id": "456"}]},
    )


def test_create_record_success(r_mock):
    table_name = "Fake"
    mock_create_record(r_mock, table_name)

    id = airtable.create_record("123", table_name, {})
    assert id is not None


def test_create_record_fail(r_mock):
    table_name = "Fake"
    r_mock.post(
        airtable.table_api_url(table_name),
        json={},
        status=404,
    )

    with pytest.raises(RuntimeError):
        airtable.create_record("123", table_name, {})


def test_upsert_record_doesnt_exist_success(r_mock):
    table_name = "Fake"

    r_mock.get(
        airtable.table_api_url(table_name),
        match=[
            query_param_matcher(
                {"maxRecords": 1, "filterByFormula": "{myattr} = 'foo'"}
            )
        ],
        json={"records": []},
    )

    mock_create_record(r_mock, table_name)

    id = airtable.upsert_record("123", table_name, "myattr", {"myattr": "foo"})
    assert id is not None


def test_upsert_record_exists_success(r_mock):
    table_name = "Fake"

    r_mock.get(
        airtable.table_api_url(table_name),
        match=[
            query_param_matcher(
                {"maxRecords": 1, "filterByFormula": "{myattr} = 'foo'"}
            )
        ],
        json={"records": [{"id": "456"}]},
    )

    id = airtable.upsert_record("123", table_name, "myattr", {"myattr": "foo"})
    assert id == "456"
