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
DEFAULT_TOP_K = 6

# Lower rank wins when docs disagree. Org-wide rules and the change log
# outrank the catalog and team playbooks; the 2023 IT FAQ ranks lowest.
AUTHORITY_RANK = {
    "03-code-review-and-prs.md": 1,
    "06-org-changes-2026.md": 1,
    "01-environments-and-access.md": 2,
    "07-deploys-releases-oncall.md": 2,
    "00-README-engineering-onboarding.md": 3,
    "08-glossary-and-common-questions.md": 3,
    "05-service-catalog-and-owners.md": 4,
    "04-payments-team-playbook.md": 4,
    "02-it-helpdesk-faq.md": 5,
}