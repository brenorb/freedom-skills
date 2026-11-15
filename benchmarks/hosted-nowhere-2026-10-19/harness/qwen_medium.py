#!/usr/bin/env python3
"""Fresh SOMP Qwen runs at medium effort; all other suite behavior is unchanged."""
import suite

if __name__ == '__main__':
    suite.MODEL_CONFIG['qwen']['thinking'] = 'medium'
    suite.MODEL_CONFIG['qwen']['native_system_context'] = True
    suite.main()
