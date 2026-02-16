"""
Survey questions - versioned for longitudinal consistency.

Version history:
  v1 - Initial single-question Likert scale (2026-02)
"""

SURVEY_VERSION = 1

QUESTION = {
    "id": "internal_coverage",
    "version": SURVEY_VERSION,
    "text": """
This scan checked for: TUF, in-toto, SBOM, and gittuf.

Compared to what's publicly visible in this repo, how complete is
your organization's INTERNAL implementation of these mechanisms?

  1 - Much less complete than public
  2 - Somewhat less complete
  3 - About the same
  4 - Somewhat more complete
  5 - Much more complete

  0 - Prefer not to answer
""",
    "options": {
        0: "Prefer not to answer",
        1: "Much less complete",
        2: "Somewhat less complete", 
        3: "About the same",
        4: "Somewhat more complete",
        5: "Much more complete",
    },
    "valid_range": (0, 5),
}