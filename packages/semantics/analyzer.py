from textx import get_line_col
from packages.diagnostics.core import DiagnosticsCollector


class SemanticAnalyzer:
    def __init__(self):
        # the symbol table
        self.programs = set()
        self.courses = {}  # code -> AST node
        self.blocks = set()

        # Dependency graph for cycle detection
        self.graph = {}  # code -> list of prerequisite codes

        self.diagnostics = DiagnosticsCollector()

    def analyze(self, ast_model):
        """Executes the multi-pass semantic analysis"""
        self._pass1_declarations(ast_model)
        self._pass2_resolutions(ast_model)
        self._pass3_cycle_detection()
        return self.diagnostics

    def _pass1_declarations(self, ast_model):
        """
        Registers all programs, courses, and blocks in the symbol tables and
        checks for duplicate declarations.
        """
        for statement in ast_model.statements:
            node_type = statement.__class__.__name__
            line, col = get_line_col(statement)

            if node_type == "CREATE_PROGRAM":
                # Simplified for MVP - just track program names
                self.programs.add(statement.name)
            elif node_type == "CREATE_COURSE":
                if statement.code in self.courses:
                    self.diagnostics.add_error(
                        code="SYL_ERR_DUPLICATE_COURSE",
                        message=f"Course code '{statement.code}' is declared multiple times.",
                        line=line,
                        col=col,
                        hint=f"Ensure '{statement.code}' is created only once.",
                    )
                else:
                    self.courses[statement.code] = statement
                    self.graph[statement.code] = []  # Initialize graph entry
            elif node_type == "CREATE_BLOCK":
                self.blocks.add(statement.name)

    def _pass2_resolutions(self, ast_model):
        """
        Resolves all references to courses and blocks, ensuring they exist.
        Also builds the dependency graph for courses based on prerequisites.
        """
        for statement in ast_model.statements:
            node_type = statement.__class__.__name__
            line, col = get_line_col(statement)

            if node_type == "CREATE_COURSE":
                # Does the target course exist?
                if statement.target_code not in self.courses:
                    self.diagnostics.add_error(
                        code="SYL_ERR_UNDEFINED_COURSE",
                        message=f"Cannot add requirements to undefined course '{statement.target_code}'.",
                        line=line,
                        col=col,
                        hint=f"Did you forget to 'CREATE COURSE ... {statement.target_code}'?",
                    )
                    continue

                # Do the prerequisite courses exist?
                for prereq in statement.prereq_codes:
                    if prereq not in self.courses:
                        self.diagnostics.add_error(
                            code="SYL_ERR_UNDEFINED_COURSE",
                            message=f"Course '{statement.target_code}' requires {prereq}, but {prereq} is not in the catalog.",
                            line=line,
                            col=col,
                            hint=f"Check your spelling or declare '{prereq}' before using 'COURSE ... REQUIRES ...'.",
                        )
                    else:
                        # Build the dependency graph for cycle detection
                        self.graph[statement.target_code].append(prereq)

    def _pass3_cycle_detection(self):
        """
        DFS to detect cycles in the course prerequisite graph. If a cycle is
        found, report an error.
        """
        visited = set()
        rec_stack = set()

        def dfs(node_code, path_nodes):
            visited.add(node_code)
            rec_stack.add(node_code)
            path_nodes.append(node_code)

            for prereq in self.graph.get(node_code, []):
                if prereq not in visited:
                    if dfs(prereq, path_nodes):
                        return True
                elif prereq in rec_stack:
                    # Cycle detected
                    cycle_path = " -> ".join(
                        path_nodes[path_nodes.index(prereq) :] + [prereq]
                    )

                    # We attach the error to the course node that triggered it
                    ast_node = self.courses[node_code]
                    line, col = get_line_col(ast_node)
                    self.diagnostics.add_error(
                        code="SYL_ERR_CYCLE_DETECTED",
                        message=f"Circular prerequisite detected involving '{prereq}'.",
                        line=line,
                        column=col,
                        hint=f"Cycle: {cycle_path}. A course cannot require itself.",
                    )
                    return True

            rec_stack.remove(node_code)
            path_nodes.pop()
            return False

        for course_code in list(self.courses.keys()):
            if course_code not in visited:
                if dfs(course_code, []):
                    break  # Stop after the first cycle is found for clearer diagnostics
