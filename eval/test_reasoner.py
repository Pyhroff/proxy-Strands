from agent import reasoner


def test_strands_action_validation_normalizes_selector():
    result = reasoner._validate(
        {"action_type": "type", "payload": {"selector": "full_name", "text": "Jane Doe"},
         "reason": "Filling the name field."},
        ["full_name"], "submit")
    assert result["payload"]["selector"] == "#full_name"
    assert result["provider"] == "Strands"


def test_invalid_submit_target_is_rejected():
    try:
        reasoner._validate({"action_type": "submit", "payload": {"selector": "#other"}}, [], "submit")
    except ValueError:
        return
    assert False, "invalid submit target was accepted"


def test_local_fallback_is_safe():
    result = reasoner._fallback(["full_name"], set(), "submit")
    assert result["action_type"] == "type"
    assert result["payload"]["selector"] == "#full_name"
