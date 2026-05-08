import os
import sys

# Ensure Python can find the packages directory when running as a module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.parser.core import SyllogosParser

def test_scenario_a_valid_program():
    dsl_text = """
    # This is our Scenario A Smoke Test
    CREATE PROGRAM "Software Engineering"

    CREATE COURSE "Programming I", CS101 WITH CREDITS 4 IN PROGRAM "Software Engineering"
    CREATE COURSE "Programming II", CS102 WITH CREDITS 4 IN PROGRAM "Software Engineering"

    # Testing our new declarative prerequisite syntax
    COURSE CS102 REQUIRES CS101

    CREATE BLOCK "Semester 1" IN PROGRAM "Software Engineering"
    ADD COURSE CS101 TO BLOCK "Semester 1"
    """

    parser = SyllogosParser()
    ast = parser.parse_text(dsl_text)

    # Validate the AST Structure
    assert ast is not None
    assert len(ast.statements) == 6 # 6 active statements (comments are ignored)

    # Check the first statement (CREATE PROGRAM)
    stmt_1 = ast.statements[0]
    assert stmt_1.__class__.__name__ == 'CREATE_PROGRAM'
    assert stmt_1.name == "Software Engineering"

    # Check the second statement (CREATE COURSE)
    stmt_2 = ast.statements[1]
    assert stmt_2.__class__.__name__ == 'CREATE_COURSE'
    assert stmt_2.name == "Programming I"
    assert stmt_2.code == "CS101"
    assert stmt_2.credits == 4

    # Check Prerequisite (Now CourseRequirement)
    stmt_4 = ast.statements[3]
    assert stmt_4.__class__.__name__ == 'ADD_PREREQUISITE'
    assert stmt_4.target_code == "CS102"
    
    # Because we used `+=` in the grammar, prereq_codes is a List!
    assert isinstance(stmt_4.prereq_codes, list)
    assert "CS101" in stmt_4.prereq_codes

    print("✅ Parser successfully generated the AST!")

if __name__ == "__main__":
    test_scenario_a_valid_program()