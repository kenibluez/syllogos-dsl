import json
from typing import Dict, Any


class IRGenerator:
    def __init__(self, semantic_analyzer):
        """
        The IR Generator strictly consumes the validated state from the Semantic Analyzer.
        It assumes Phase 1-3 have already run
        """
        self.analyzer = semantic_analyzer
        self.ir: Dict[str, Any] = {
            "version": "1.0",
            "programs": [],
            "courses": [],
            "blocks": [],
            "edges": [],
        }

    def generate(self) -> Dict[str, Any]:
        """
        Transforms the semantic model into a structured Intermediate Representation (IR).
        Internal symbol tables are flattened into a JSON-serializable format.
        """

        # Map programs
        for prog_name in sorted(list(self.analyzer.programs)):
            self.ir["programs"].append(
                {
                    "id": prog_name,
                    "name": prog_name,
                }
            )

        # Map Courses (the catalog)
        for code, node in self.analyzer.courses.items():
            course_data = {
                "code": code,
                "name": node.name,
                "credits": node.credits,
                "program_id": node.program,
            }
            self.ir["courses"].append(course_data)

        # Sort for deterministic output
        self.ir["courses"].sort(key=lambda x: x["code"])

        # Map Blocks
        for label in sorted(list(self.analyzer.blocks)):
            self.ir["blocks"].append({"id": label, "name": label})

        # Map Edges (the dependency graph)
        # The analyzer.graph contains adjacency lists: target_code -> [prereq1, prereq2]
        for target_code, prereqs in self.analyzer.graph.items():
            for prereq in prereqs:
                self.ir["edges"].append(
                    {"source": prereq, "target": target_code, "type": "prerequisite"}
                )

        # Sort edges for deterministic output
        self.ir["edges"].sort(key=lambda x: (x["source"], x["target"]))

        return self.ir

    def to_json(self) -> str:
        """Returns the IR as a formatted JSON string."""
        return json.dumps(self.generate(), indent=2)
