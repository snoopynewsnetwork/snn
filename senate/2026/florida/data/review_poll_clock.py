"""Check retained primary polling-clock evidence without changing the contract."""
import datetime
import gzip
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data/turnout/source"


def source(name):
    receipt_path = SOURCES / (name + ".receipt.json")
    receipt = json.loads(receipt_path.read_text())
    body_path = SOURCES / (name + ".body.gz")
    stored = body_path.read_bytes()
    raw = gzip.decompress(stored)
    assert receipt["status"] == 200
    assert hashlib.sha256(stored).hexdigest() == receipt["stored_sha256"]
    assert hashlib.sha256(raw).hexdigest() == receipt["raw_sha256"]
    assert len(raw) == receipt["raw_bytes"]
    text = html.unescape(re.sub(r"<[^>]*>", " ", raw.decode("utf-8")))
    text = " ".join(text.split())
    return text, {
        "receipt_path": str(receipt_path.relative_to(ROOT)),
        "body_path": str(body_path.relative_to(ROOT)),
        "receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        "raw_sha256": receipt["raw_sha256"],
        "stored_sha256": receipt["stored_sha256"],
        "url": receipt["final_url"],
        "retrieved_utc": receipt["retrieved_utc"],
    }


law, law_pin = source("poll-hours-law")
county, county_pin = source("gulf-election-day")
assert "2026 Florida Statutes" in law
assert "customary time in standard use in the county seat of the locality" in law
assert "Election Day Voting Schedule" in county
assert "Polls open at 7:00 AM (ET), 6:00 AM (CT)" in county
assert "Polls close at 7:00 PM (ET), 6:00 PM (CT)" in county
contract = ROOT / "data/turnout/priority-set.json"
assert hashlib.sha256(contract.read_bytes()).hexdigest() == "0c056e0ebfdb393d4fcb59676805122d8442f444200b9edaf7f4c979c5e9a173"
result = {
    "status": "pass_with_election_specific_recheck",
    "reviewed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "sources": [law_pin, county_pin],
    "finding": "Section100.011(1) uses county-seat customary standard time. Gulf publishes one simultaneous7pmEastern/6pmCentral polling close; physical geographic split alone does not imply separate closing instants.",
    "correction": "Coordinator's earlier inference that geographic split prevented a singular countywide schedule was overbroad. No historical count, rank, native identity, accepted witness or frozen contract was changed.",
    "contract_operational_fields": "Remain null deliberately; historical dispatch acceptance grants no operational clock authority.",
    "remaining_checks": ["Election-specific November notice and any later extension", "Separate office, vote-by-mail and exceptional ballot receipt rules"],
}
(ROOT / "data/coordinator-poll-clock-review.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": result["status"], "sources": len(result["sources"]), "contract_unchanged": True}))
