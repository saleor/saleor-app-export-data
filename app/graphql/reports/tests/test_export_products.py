from unittest import mock

import pytest
from gql.transport.exceptions import TransportQueryError

from app.core.export.fetch import fetch_report_by_id
from app.core.reports.models import ExportObjectTypesEnum

MUTATION_EXPORT_PRODUCTS = """
mutation ProductsExport($input: ExportProductsInput!) {
    exportProducts (input: $input) {
        __typename
        ...  on Report {
            id
            type
        }
        ... on  ExportErrorResponse{
            code
            message
            field
        }
    }
}
"""


@pytest.mark.asyncio
@mock.patch("app.graphql.reports.mutations.products.init_export_for_report")
async def test_export_products_schedules_task(m_task, graphql):
    # given
    variables = {
        "input": {
            "columns": {
                "fields": ["ID", "VARIANT_ID"],
            },
        }
    }
    # when
    result = await graphql.execute(MUTATION_EXPORT_PRODUCTS, variables)
    # then
    assert (
        result["data"]["exportProducts"]["type"] == ExportObjectTypesEnum.PRODUCTS.name
    )
    assert m_task.delay.call_count == 1


@pytest.mark.asyncio
@mock.patch("app.graphql.reports.mutations.products.init_export_for_report")
async def test_export_products_without_optional_columns(m_task, db_session, graphql):
    # given
    variables = {
        "input": {
            "columns": {
                "fields": ["ID", "VARIANT_ID"],
            },
        }
    }
    # when
    result = await graphql.execute(MUTATION_EXPORT_PRODUCTS, variables)
    # then
    report_id = result["data"]["exportProducts"]["id"]
    report = await fetch_report_by_id(db_session, report_id)
    assert len(report.columns["fields"]) == 2
    assert len(report.columns["attributes"]) == 0
    assert len(report.columns["warehouses"]) == 0
    assert len(report.columns["channels"]) == 0


@pytest.mark.asyncio
@mock.patch("app.graphql.reports.mutations.products.init_export_for_report")
async def test_export_products_wit_related_columns(m_task, db_session, graphql):
    # given
    fields = ["ID", "VARIANT_ID"]
    channel_ids = ["1", "2", "3"]
    warehouse_ids = ["4", "5", "6"]
    attribute_ids = ["7", "8", "9"]
    variables = {
        "input": {
            "columns": {
                "fields": fields,
                "channels": channel_ids,
                "warehouses": warehouse_ids,
                "attributes": attribute_ids,
            },
        }
    }
    # when
    result = await graphql.execute(MUTATION_EXPORT_PRODUCTS, variables)
    # then
    report_id = result["data"]["exportProducts"]["id"]
    report = await fetch_report_by_id(db_session, report_id)
    assert report.columns["fields"] == fields
    assert report.columns["attributes"] == attribute_ids
    assert report.columns["warehouses"] == warehouse_ids
    assert report.columns["channels"] == channel_ids


@pytest.mark.asyncio
@pytest.mark.parametrize("input_field", ["attributes", "warehouses"])
@mock.patch("app.graphql.reports.mutations.products.init_export_for_report")
async def test_export_products_exceeds_column_limit(m_task, graphql, input_field):
    # given
    variables = {
        "input": {
            "columns": {
                "fields": ["ID", "VARIANT_ID"],
                input_field: [str(i) for i in range(101)],
            },
        }
    }
    # when
    result = await graphql.execute(MUTATION_EXPORT_PRODUCTS, variables)
    # then
    assert result["data"]["exportProducts"]["__typename"] == "ExportErrorResponse"
    assert result["data"]["exportProducts"]["field"] == input_field
    assert result["data"]["exportProducts"]["code"] == "LIMIT_EXCEEDED"


@pytest.mark.asyncio
@mock.patch("app.graphql.reports.mutations.products.init_export_for_report")
async def test_export_products_invalid_filter_json(m_task, graphql):
    # given
    variables = {
        "input": {
            "columns": {"fields": ["ID", "VARIANT_ID"]},
            "filter": {"filterStr": "{not a real json}"},
        },
    }
    # when
    result = await graphql.execute(MUTATION_EXPORT_PRODUCTS, variables)
    # then
    assert result["data"]["exportProducts"]["code"] == "INVALID_FILTER"
    assert m_task.delay.call_count == 0


@pytest.mark.asyncio
@mock.patch("app.graphql.reports.mutations.products.fetch_products_response")
@mock.patch("app.graphql.reports.mutations.products.init_export_for_report")
async def test_export_products_remote_graphql_error(m_task, m_fetch, graphql):
    # given
    msg = "remote error"
    m_fetch.side_effect = TransportQueryError(msg)
    variables = {
        "input": {
            "columns": {"fields": ["ID", "VARIANT_ID"]},
            "filter": {"filterStr": '{"notReal": "but json"}'},
        },
    }
    # when
    result = await graphql.execute(MUTATION_EXPORT_PRODUCTS, variables)
    # then
    assert result["data"]["exportProducts"]["code"] == "INVALID_FILTER"
    assert result["data"]["exportProducts"]["message"] == msg
    assert m_task.delay.call_count == 0
