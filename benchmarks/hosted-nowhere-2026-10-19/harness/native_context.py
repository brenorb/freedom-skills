#!/usr/bin/env python3
"""Retain native Claude/SOMP agent instructions with the isolated benchmark tools."""
import suite

if __name__ == '__main__':
    for model in ['haiku', 'qwen']:
        suite.MODEL_CONFIG[model]['native_system_context'] = True
    suite.main()
