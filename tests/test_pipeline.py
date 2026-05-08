import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from packages.parser.core import SyllogosParser
from packages.semantics.analyzer import SemanticAnalyzer
from packages.ir.generator import IRGenerator


def compile_syllogos(source_text: str):
    print("🚀 Starting Syllogos Compiler Pipeline...")

    # Phase 2: Parse -> AST
    parser = SyllogosParser()
    try:
        ast = parser.parse_text(source_text)
    except ValueError as e:
        print(e)
        return

    # Phase 3: Semantic Analysis
    analyzer = SemanticAnalyzer()
    diagnostics = analyzer.analyze(ast)

    # Phase 4: Diagnostics Evaluation
    if diagnostics.has_errors():
        print("\n❌ Compilation Failed. Semantic errors detected:")
        diagnostics.report()
        return  # Halt pipeline on semantic errors

    print("✅ Semantics Validated.")

    # Phase 5: IR Generation
    generator = IRGenerator(analyzer)
    ir_json = generator.to_json()

    print("\n📦 Compilation Successful! Stable IR Generated:")
    print(ir_json)


if __name__ == "__main__":
    # A perfectly valid, complex curriculum snippet
    valid_dsl = """
    CREATE PROGRAM "Computer Science"

    CREATE COURSE "Intro to Programming", CS101 WITH CREDITS 4 IN PROGRAM "Computer Science"
    CREATE COURSE "Data Structures", CS201 WITH CREDITS 4 IN PROGRAM "Computer Science"
    CREATE COURSE "Algorithms", CS301 WITH CREDITS 3 IN PROGRAM "Computer Science"

    COURSE CS201 REQUIRES CS101
    COURSE CS301 REQUIRES CS201, CS101

    CREATE BLOCK "Semester 1" IN PROGRAM "Computer Science"
    ADD COURSE CS101 TO BLOCK "Semester 1"
    """
    compile_syllogos(valid_dsl)
