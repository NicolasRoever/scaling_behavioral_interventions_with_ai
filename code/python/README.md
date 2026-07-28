# Python workflow

Install `requirements.txt` and run scripts from this directory. The exhibit
crosswalk is in `../../EXHIBIT_MANIFEST.md`.

The public package supports two levels of verification:

1. Downstream plotting and tabulation from included survey data and minimized,
   text-free derived files.
2. Inspection of the full topic-modeling, language-analysis, and MITI-scoring
   code.

Fresh BERTopic fitting, interviewer-language analysis, and LLM scoring require
the private interview corpus and therefore cannot be rerun here. The absent
input is marked by `../../data/private/interview_transcripts.txt`.

All notebooks in this package have had stored outputs and execution counts
removed to prevent accidental disclosure of interview text.

