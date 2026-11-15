#!/usr/bin/env python3
"""Fresh SOMP replay with compact context and repository workflow guidance."""
import suite


def configure():
    suite.MODEL_CONFIG['qwen']['thinking'] = 'medium'
    suite.MODEL_CONFIG['qwen']['native_system_context'] = False
    suite.SYSTEM += '''
Workflow priority, reflecting the repository's action-first guidance:
Prepare necessary input from the selected skill reference, then execute the
command matching the user's goal. The application CLI is known-good here.
Fall back to its targeted help or environment checks when that action fails,
or an essential input or command detail is genuinely missing. Do not turn
implementation-code research or setup verification into a preflight stage.
Each bash invocation starts a fresh shell; persist values in workspace files
or set them again within each invocation.
Continue following the browser tool's required API-reading and observation
instructions. This is an operation task using the skill's workflows.
'''


if __name__ == '__main__':
    configure()
    suite.main()
