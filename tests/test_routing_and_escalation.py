"""Graph routing and escalation tiering — offline, no model calls."""
import pytest
from langgraph.graph import END

from agents.escalation_agent import determine_escalation_tier
from agents.orchestrator import route_after_intake, route_after_monitoring


# ── Routing ──────────────────────────────────────────────────────────────────

def test_red_check_in_routes_to_escalation():
    assert route_after_monitoring({"current_agent": "escalation_agent"}) == "escalation_agent"


@pytest.mark.parametrize("state", [{"current_agent": "admin_agent"}, {}])
def test_green_or_yellow_check_in_routes_to_admin(state):
    assert route_after_monitoring(state) == "admin_agent"


def test_unparseable_pdf_stops_before_care_plan():
    assert route_after_intake({"active_flags": ["PDF_PARSE_FAILED: no text"]}) == END


def test_parsed_pdf_continues_to_care_plan():
    assert route_after_intake({"active_flags": []}) == "care_plan_agent"


# ── Escalation tier (keyword matching) ──────────────────────────────────────

def responses(text):
    return {"how_are_you_feeling": text}


@pytest.mark.parametrize("text, expected", [
    ("I have chest pain and I'm sweating", "TIER_3"),
    ("my husband noticed some confusion this morning", "TIER_2"),
    ("I feel a bit tired", "TIER_1"),
])
def test_keyword_tiers(text, expected):
    assert determine_escalation_tier([], responses(text), {}) == expected


def test_flags_count_as_well_as_responses():
    assert determine_escalation_tier(["Patient reports stroke symptoms"], {}, {}) == "TIER_3"


def test_paraphrased_emergency_is_under_tiered():
    """Known limitation, fixed in Hub v2: no literal keyword means no TIER_3."""
    assert determine_escalation_tier([], responses("I feel like I'm suffocating"), {}) != "TIER_3"
