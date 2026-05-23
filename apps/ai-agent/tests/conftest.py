import sys
import os

# Make sure 'agents', 'memory', 'schemas', 'prompts' are importable during pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
