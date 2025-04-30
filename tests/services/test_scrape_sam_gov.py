from typing import Any

from rfp_scraper.services.scrape_sam_gov import SamGovSearchResponse


def test_sam_gov_opportunities_validation_basic(sam_gov_api_response_json_basic: dict[str, Any]):
    opportunities = SamGovSearchResponse.model_validate(sam_gov_api_response_json_basic)
    assert len(opportunities.opportunitiesData) == 1
    assert opportunities.opportunitiesData[0].noticeId == "f5ee2b7d16634065b904c6943bb0c0eb"


def test_sam_gov_opportunities_validation_complex(sam_gov_api_response_json_complex: dict[str, Any]):
    opportunities = SamGovSearchResponse.model_validate(sam_gov_api_response_json_complex)
    assert len(opportunities.opportunitiesData) == len(sam_gov_api_response_json_complex["opportunitiesData"])
