#!/usr/bin/env python3
"""Compact SOMP replay prioritizing the selected reference's completion record."""
import suite
from qwen_action_first import configure


if __name__ == '__main__':
    configure()
    # "Verification account" means an account of the checks, not a user identity.
    wording = 'final share URL and verification account in your final response.'
    assert suite.SYSTEM.count(wording) == 1
    suite.SYSTEM = suite.SYSTEM.replace(
        wording,
        'final share URL and a brief statement describing what you verified.',
    )
    suite.SYSTEM += '''
For the final response, use the completion record provided by the selected
reference when one exists. Fill its fields only from actual observations.
Before finishing, recheck every claim of success, identity, or protection
against the saved outputs. Keep an earlier operation's success separate from
downstream outcomes that were not verified. Limit the report to the requested
deliverables and that completion record; omit speculative additions.
'''
    suite.main()
