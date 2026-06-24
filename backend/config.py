"""Central configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
CHROMA_DIR = ROOT / ".chroma"
FRONTEND_DIR = ROOT / "frontend"

EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
ANSWER_MODEL = os.getenv("ANSWER_MODEL", "claude-sonnet-4-6")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

COLLECTION_NAME = "payrails_onboarding"
CHUNK_MAX_CHARS = 1200
CHUNK_OVERLAP_CHARS = 150
# Retrieve a bit wider than strictly needed: a conflict can only be flagged if
# BOTH sides land in context, so we trade a little latency for the guarantee
# that the authoritative doc isn't pushed out of the window by a stale one.
DEFAULT_TOP_K = 8


# --- Authority model ------------------------------------------------------
# Lower rank wins when docs disagree. We rank by *document type*, not by ad-hoc
# per-file numbers, so the policy generalises: a new doc inherits the authority
# of its kind instead of needing a hand-assigned score. A doc can also override
# its tier by declaring `Authority: <n>` in its header line (see ingest.py).
class Tier:
    ORG_RULE = 1   # org-wide rules + the org-change log (authoritative by mandate)
    PLATFORM = 2   # current platform / environment / process docs
    REFERENCE = 3  # readme, glossary — helpful but summarising, not authoritative
    CATALOG = 4    # service catalog + team playbooks — local, often lags reality
    LEGACY = 5     # known-stale docs


# Unknown docs sit with the catalog/team tier: below org rules and platform docs
# so they can't accidentally override curated truth, but above known-legacy.
DEFAULT_TIER = Tier.CATALOG

DOC_TIER = {
    "03-code-review-and-prs.md": Tier.ORG_RULE,
    "06-org-changes-2026.md": Tier.ORG_RULE,
    "01-environments-and-access.md": Tier.PLATFORM,
    "07-deploys-releases-oncall.md": Tier.PLATFORM,
    "00-README-engineering-onboarding.md": Tier.REFERENCE,
    "08-glossary-and-common-questions.md": Tier.REFERENCE,
    "05-service-catalog-and-owners.md": Tier.CATALOG,
    "04-payments-team-playbook.md": Tier.CATALOG,
    "02-it-helpdesk-faq.md": Tier.LEGACY,
}


def authority_for(filename: str, declared: int | None = None) -> int:
    """Resolve a doc's authority rank.

    A doc may self-declare its rank via an `Authority:` header field (handles
    new authoritative docs with no code change). Otherwise it inherits its
    document-type tier, falling back to DEFAULT_TIER for unrecognised files.
    """
    if declared is not None:
        return declared
    return DOC_TIER.get(filename, DEFAULT_TIER)