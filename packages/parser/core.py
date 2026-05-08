import os
from textx import metamodel_from_file
from textx.exceptions import TextXSyntaxError

class SyllogosParser:
    def __init__(self):
        # Load the grammar file
        grammar_path = os.path.join(
            os.path.dirname(__file__), 
            '../grammar/syllogos.tx'
        )
        
        # ignore_case=True makes keywords like CREATE, create, and Create valid,
        # fulfilling our v0.1 case-insensitivity requirement.
        self.meta = metamodel_from_file(grammar_path, ignore_case=True)

    def parse_text(self, source_text: str):
        """
        Parses raw DSL text and returns the AST root (Model).
        Raises a formatted exception if syntax is completely invalid.
        """
        try:
            # textX parses the text and builds the AST automatically
            ast_model = self.meta.model_from_str(source_text)
            return ast_model
        except TextXSyntaxError as e:
            # In Phase 4, we will route this to the Diagnostic Engine.
            # For now, we wrap it cleanly.
            raise ValueError(f"Syntax Error at Line {e.line}, Col {e.col}: {e.message}")

    def parse_file(self, file_path: str):
        """Helper to parse directly from a file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return self.parse_text(f.read())