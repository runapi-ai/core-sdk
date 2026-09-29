"""Rule messages must match every other SDK (sdk/contract_rule_messages.json)."""

import json
from pathlib import Path

import pytest

from runapi.core import Resource
from runapi.core.errors import ValidationError

SDK_ROOT = Path(__file__).resolve().parents[4]
FIXTURE = SDK_ROOT / "contract_rule_messages.json"
CONTRACT = SDK_ROOT / "contract.json"

# The shared fixture lives in the SDK monorepo; the public package repo does not ship it.
pytestmark = pytest.mark.skipif(not FIXTURE.exists(), reason="shared SDK fixture not available")

CASES = json.loads(FIXTURE.read_text())["cases"] if FIXTURE.exists() else []


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_rule_message_matches_shared_fixture(case):
    schema = json.loads(CONTRACT.read_text())["actions"][case["action"]]

    with pytest.raises(ValidationError) as error:
        Resource(object())._validate_contract(schema, dict(case["params"]))

    assert str(error.value) == case["message"]
