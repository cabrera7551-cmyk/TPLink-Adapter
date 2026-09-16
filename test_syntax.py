#!/usr/bin/env python3
"""Test simple de sintaxis para main.py"""

import sys
import py_compile

try:
    py_compile.compile('main.py', doraise=True)
    print("Sintaxis Python válida")
    sys.exit(0)
except py_compile.PyCompileError as e:
    print(f"Error de sintaxis: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
