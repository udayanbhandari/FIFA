"""Unit tests for the rule-based assistant fallback engine."""

from __future__ import annotations

from app.assistant.rules import get_rule_based_assistance
from app.models import FanAssistantQuery, Language


def test_restroom_keywords_resolve_to_restrooms() -> None:
    """Verifies restroom questions return restroom guidance and zone references."""
    query = FanAssistantQuery(
        question="Where is the closest toilet or wc?",
        language=Language.EN,
    )
    res = get_rule_based_assistance(query)
    assert res.zone_reference == "restroom_north"
    assert "restroom" in res.answer.lower()
    assert res.confidence == 0.8


def test_medical_keywords_resolve_to_medical() -> None:
    """Confirms doctor/injury questions trigger medical action steps."""
    query = FanAssistantQuery(
        question="I need a doctor, someone is hurt!",
        language=Language.EN,
    )
    res = get_rule_based_assistance(query)
    assert res.zone_reference == "medical_main"
    assert any(act.action == "alert_steward" for act in res.suggested_actions)


def test_multilingual_templates_applied_correctly() -> None:
    """Checks Spanish and French queries return localized template responses."""
    query_es = FanAssistantQuery(
        question="¿Dónde están los baños?",
        language=Language.ES,
    )
    res_es = get_rule_based_assistance(query_es)
    assert "baños" in res_es.answer.lower()
    assert res_es.language == Language.ES

    query_fr = FanAssistantQuery(
        question="Où se trouve le centre de transport?",
        language=Language.FR,
    )
    res_fr = get_rule_based_assistance(query_fr)
    assert "transport" in res_fr.answer.lower()
    assert res_fr.language == Language.FR


def test_unknown_keywords_return_general_fallback() -> None:
    """Ensures unrecognized questions default to general welcome response."""
    query = FanAssistantQuery(
        question="Random question about tickets",
        language=Language.EN,
    )
    res = get_rule_based_assistance(query)
    assert res.zone_reference is None
    assert "fifa" in res.answer.lower()
    assert res.source == "rules"
