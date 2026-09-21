raise RuntimeError("Restricted-input source only. Raw interview data are not distributed. API execution is disabled in this $0-API replication package; use code/python/run_public.py for saved-result reproduction.")

# Canonical reusable prompts are public under code/prompts/.
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from prompts.miti_global_scores import MAIN_PROMPT, MITI_GUIDE, VALIDATION_PROMPT
