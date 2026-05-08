import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.parser.core import SyllogosParser
from packages.semantics.analyzer import SemanticAnalyzer

def test_semantic_analysis():
    dsl_text = """
    CREATE PROGRAM "Software Engineering"

    CREATE COURSE "Programming I", CS101 IN PROGRAM "Software Engineering"
    CREATE COURSE "Programming II", CS102 IN PROGRAM "Software Engineering"
    
    # 1. Undefined Error Test
    COURSE CS102 REQUIRES CS999  

    # 2. Cycle Error Test
    CREATE COURSE "Arch", CS401 IN PROGRAM "Software Engineering"
    CREATE COURSE "OS", CS402 IN PROGRAM "Software Engineering"

    COURSE CS401 REQUIRES CS402
    COURSE CS402 REQUIRES CS401
    """
    
    parser = SyllogosParser()
    ast = parser.parse_text(dsl_text)
    
    analyzer = SemanticAnalyzer()
    diagnostics = analyzer.analyze(ast)
    
    print("\n--- Semantic Analysis Diagnostics ---")
    diagnostics.report()
    
    # Assertions
    assert diagnostics.has_errors()
    error_codes = [d.code for d in diagnostics.diagnostics]
    assert "SYL_ERR_UNDEFINED_COURSE" in error_codes
    assert "SYL_ERR_CYCLE_DETECTED" in error_codes

if __name__ == "__main__":
    test_semantic_analysis()
