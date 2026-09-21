raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")

# Canonical reusable prompts are public under code/prompts/.
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from prompts.miti_behavioral_counts import MITI_MAIN_BEHAVIOR, MITI_BEHAVIOR_COUNTS_PROMPT
