# Syllogos — DSL Implementation & Development Guide (Language Core Only)

Version: 0.1 (Draft)  
Audience: Curriculum/Language engineers building the Syllogos DSL compiler ecosystem (language core only; no web app, no SaaS platform).

## 0. Scope & Non-Goals

### In Scope (Phase 1–7 language engine)
- DSL language design (domain model, minimal syntax)
- Grammar
- Parser → AST
- Semantic analysis (validation rules)
- Diagnostics
- IR generation (stable machine-readable form)
- Graph generation (dependency graph)
- CLI/tooling support for dev workflow

### Explicit Non-Goals (for now)
- Web services / HTTP API
- Authentication, persistence, multi-tenant concerns
- Scheduling, student enrollment, GPA, payment, UI/Monaco integration

---

## 1. Vision & Core Philosophy

Syllogos is a **human-readable DSL** for defining, validating, and analyzing university curricula.

It should feel like academic documentation with machine-level strictness:
- Readable by professors
- Writable by curriculum designers
- Analyzable by machines
- Strict semantically
- Visually clean and indentation-driven

### Key Principles
1. Human readability first
2. Declarative, not imperative
3. Semantic clarity over clever syntax
4. Educational diagnostics (actionable, line/column, hints)
5. Stable pipeline: Source → AST → Semantics → Diagnostics → IR → Graph

---

## 2. High-Level Architecture (Language Core)

### 2.1 Logical Services/Pipeline
Even if implemented as libraries, design the modules as if they were services:

```txt
Source
  → Lexer (if needed)
  → Parser
  → AST
  → Semantic Analysis
  → Validation Engine
  → Diagnostic Engine
  → IR Generator
  → Graph Engine
  → (CLI output / tests)
```

### 2.2 Module Responsibilities
- **Parser**: produces AST from DSL text
- **AST**: typed representation of program elements
- **Semantic Analyzer**: builds symbol tables, resolves references, checks structural constraints
- **Validation Engine**: checks domain rules (credits, prerequisites, duplicates, cycles, semester consistency, etc.)
- **Diagnostic Engine**: collects structured diagnostics with line/column and hints
- **IR Generator**: converts AST into stable IR (frontend/tools consume IR, not AST)
- **Graph Engine**: converts prerequisites/requirements into dependency graph form

### 2.3 Design Pattern Defaults
- **Pipeline/Compiler Passes**: each phase receives output of previous phase
- **Visitor Pattern (or pattern-matching traversal)** over AST for analysis/IR
- **Symbol Table** for reference resolution
- **Error Accumulation** (never “fail fast” on first error; collect as much as possible)
- **Pure Functions for transforms** where feasible (AST→IR, AST→Graph)
- **Deterministic output**: stable ordering in IR and graph edges

---

## 3. Repository Layout (Monorepo)

Suggested structure (language core only):

```txt
syllogos/
├── apps/
│   └── cli/                         # optional: dev CLI entrypoint for compile/graph
│
├── packages/
│   ├── grammar/                     # grammar definitions + parser generation or textX config
│   ├── parser/                      # parser wrapper producing AST + source positions
│   ├── ast/                         # AST node types + helpers
│   ├── semantics/                  # symbol tables, reference resolution, semantic checks
│   ├── diagnostics/                # Diagnostic type, formatting, aggregation
│   ├── validation/                 # higher-level validation rules
│   ├── ir/                          # IR schema + generator
│   └── graph/                       # dependency graph structures + algorithms
│
├── examples/
│   ├── software-engineering.dsl
│   └── invalid-examples/
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── docs/
│   ├── language/
│   │   ├── design-philosophy.md
│   │   ├── semantics.md
│   │   └── diagnostics.md
│   └── development/
│       ├── conventions.md
│       └── release.md
│
├── .github/                        # CI workflows
├── scripts/                        # dev scripts
├── package.json                    # workspace root (optional if using TS tooling)
├── pnpm-lock.yaml                  # or yarn.lock/npm-lock (choose one)
├── tsconfig.json                   # if TS is used anywhere
└── pyproject.toml                  # if Python is used anywhere
```

### Implementation language choice
Your outline suggests **textX** for grammar. This guide supports a hybrid approach:
- **Python**: textX grammar + parser (AST with positions)
- **TypeScript**: IR/graph/diagnostics formatting and tests (optional)
- Or all-Python/all-TS. Pick one early to avoid churn.

To keep closer to your outline: below we assume **Python for grammar/parser**, and **TypeScript for IR/graph/diagnostics output** (optional). If you prefer single-language, say so and we’ll re-map modules.

---

## 4. DSL: Domain Model (Language Semantics)

### 4.1 Core Entities
- **Program**
- **Semester** (ordered or numbered)
- **Course**
  - code
  - name
  - credits
  - prerequisites (by code reference)
- **Requirement / Elective group** (future extension; can be stubbed now)
- **Constraints** (future expansion; MVP may include max credits per semester)

### 4.2 Minimal MVP Syntax (Indentation-based)
MVP should include:
- programs
- semesters
- courses
- prerequisites
- validation + diagnostics
- graph generation

Example:

```dsl
program "Software Engineering"

semester 1:
    course CS101:
        name "Programming I"
        credits 4

semester 2:
    course CS102:
        name "Programming II"
        credits 4

        requires:
            CS101
```

---

## 5. Language Surface Design Rules

### 5.1 Indentation-Based Blocks
- Blocks are determined by indentation (e.g., 4 spaces recommended)
- No braces; keep punctuation minimal
- Use explicit keywords: `program`, `semester`, `course`, `name`, `credits`, `requires`

### 5.2 Naming Rules
- Course codes follow a simple pattern for MVP (recommended):
  - uppercase letters + digits, e.g., `CS101`
- Course names are string literals

### 5.3 Reserved Keywords (MVP)
- `program`, `semester`, `course`, `name`, `credits`, `requires`, `elective`, `group`, `choose`, `courses`, `max`

(Keep list small initially; expand as features are added.)

---

## 6. Compiler Pipeline: Interfaces Between Phases

Design “pass interfaces” so each phase is independently testable.

### 6.1 Suggested Core Types (language-agnostic)
- `SourceFile`: `{ path?, text }`
- `ASTProgram`: AST root with node positions
- `Diagnostic`: structured error/warning
- `IRProgram`: stable machine-readable model
- `IRGraph`: nodes + edges and metadata

### 6.2 Diagnostic Shape (required)
Diagnostics must include:
- `severity` (`error`, `warning`, `info`)
- `message` (educational)
- `line`, `column`
- `hint` (optional)
- `code` (optional stable diagnostic id for tests)

---

## 7. Module Breakdown (Implementation Details)

### 7.1 grammar/
**Purpose:** DSL grammar definition for MVP.

Deliverables:
- Grammar specification compatible with your chosen tool (e.g., textX)
- Clear mapping from grammar rules to AST nodes

Design constraints:
- Keep grammar simple
- Add features only when preceding phases are stable

### 7.2 parser/
**Purpose:** parse text into AST with source positions.

Responsibilities:
- Provide a `parse(sourceText) -> ASTProgram`
- Attach line/column info to nodes used in diagnostics

Key requirement:
- Do not discard positional info during AST creation

### 7.3 ast/
**Purpose:** typed AST nodes.

Provide:
- Node classes/interfaces (e.g., ProgramNode, SemesterNode, CourseNode)
- Common base node with `start/end` position

Recommended AST traversal helper(s):
- `walk(node, visitor)` or visitor base class

### 7.4 semantics/
**Purpose:** semantic analysis (symbol tables, reference resolution, structural checks).

Responsibilities:
- Build `course registry` symbol table
  - key: course code
  - value: declared course node + position
- Resolve `requires:` course references
- Detect cycles in prerequisite graph (DFS or later graph module)
- Detect duplicates (same course code appears multiple times)

### 7.5 validation/
**Purpose:** additional validation rules beyond reference resolution.

Examples (MVP):
- credits must be positive integer
- prerequisites must reference defined courses
- semester consistency rules (optional MVP)
- cycle errors

Make validation a separate layer so semantics resolution stays focused.

### 7.6 diagnostics/
**Purpose:** centralized diagnostic aggregation and formatting.

Responsibilities:
- `DiagnosticCollector` that supports:
  - `add(diag)`
  - `merge(otherCollector)`
- Format diagnostics for CLI and tests

### 7.7 ir/
**Purpose:** AST → IR.

Rules:
- IR should be stable and versioned
- Frontends should consume IR, not AST
- IR ordering should be deterministic

IR example (conceptual):

```json
{
  "program": { "name": "Software Engineering" },
  "semesters": [],
  "courses": [],
  "edges": [
    { "from": "CS101", "to": "CS102", "kind": "prerequisite" }
  ],
  "diagnostics": []
}
```

### 7.8 graph/
**Purpose:** graph algorithms and graph output.

Responsibilities:
- Build dependency graph from IR edges
- Provide analysis outputs:
  - topological order (if acyclic)
  - cycle detection (if not already done)
  - bottleneck analysis (later)

---

## 8. CI/CD, Testing, and Quality Gates

### 8.1 CI (Recommended)
Use GitHub Actions (or your CI provider) to run:
- lint/format checks
- unit tests
- integration tests
- type checks (if TS used)

Example workflow steps:
1. Install dependencies
2. Run formatter in check mode
3. Run linter
4. Run unit tests
5. Run integration tests
6. Build (if applicable)

### 8.2 Testing Strategy

#### Unit Tests (fast)
- grammar parsing tests (valid + invalid syntax)
- semantic analyzer:
  - undefined prerequisite detection
  - duplicate course codes
  - credit validation
  - reference resolution
- diagnostics formatting tests

#### Integration Tests (DSL → IR → Graph)
- compile sample DSL file
- assert:
  - number of diagnostics
  - IR contains expected courses/edges
  - graph outputs expected order or cycle errors

### 8.3 Test Fixtures
- `examples/valid/*.dsl`
- `examples/invalid/*.dsl` with expected diagnostic snapshots
- store expected diagnostics as JSON snapshots (stable message ids help)

---

## 9. Tooling & Configuration

### 9.1 Formatter/Linter/Typecheck (recommended)
Choose defaults and enforce in CI:

- Python:
  - formatter: Black
  - linter: Ruff
  - type checker: (optional) mypy or pyright
- TypeScript (if used):
  - formatter: Prettier
  - linter: ESLint
  - type checker: `tsc --noEmit`

### 9.2 Workspace Package Manager
Pick one:
- pnpm (recommended for monorepos)
- npm workspaces
- yarn

Document it in root `README.md`.

### 9.3 tsconfig / pyproject
- `tsconfig.json`:
  - strict mode recommended
  - output settings per package
- `pyproject.toml`:
  - dependencies grouped by dev/runtime
  - tool configs for Ruff/Black

---

## 10. Virtual Environment Procedure (Dev Guide)

This guide assumes Python components (textX + parser) are in the repo.

### Option A: Root venv (simple)
1. Create venv:
   - `python -m venv .venv`
2. Activate:
   - macOS/Linux: `source .venv/bin/activate`
   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
3. Install deps:
   - `pip install -r requirements-dev.txt` (or `pip install -e .[dev]`)
4. Run:
   - `pytest`

### Option B: `uv` (faster, recommended if available)
1. Install uv:
   - follow uv install instructions
2. Create environment:
   - `uv sync`
3. Activate:
   - `uv run ...` for one-off commands

(Use Option A if you want maximum compatibility.)

---

## 11. CLI / Developer Workflow (Language Core Only)

Add a CLI in `apps/cli/` (optional but strongly useful).

Commands (examples):
- `syllogos compile path/to/file.dsl`
  - outputs:
    - diagnostics to stderr
    - IR JSON to stdout or a file
- `syllogos graph path/to/file.dsl`
  - outputs graph JSON
- `syllogos validate path/to/file.dsl`
  - exits non-zero on errors

Design:
- CLI must not require web dependencies
- CLI should share the same pipeline as tests

---

## 12. Coding Conventions & Contribution Rules

### 12.1 Language conventions
- Indentation: 4 spaces in DSL examples
- DSL file examples: keep them short and readable
- AST/IR property naming:
  - prefer `snake_case` or `camelCase` consistently by language choice
- IDs:
  - stable diagnostic codes (e.g., `SYL_ERR_UNDEFINED_COURSE`)

### 12.2 Commit conventions
Use **Conventional Commits**:
- `feat(parser): add indentation rules`
- `fix(semantics): report undefined prerequisites with hint`
- `test: add integration fixture for cycles`

### 12.3 Versioning
- Use SemVer for the language core
- Suggested approach:
  - `MAJOR`: breaking changes to IR schema or grammar syntax
  - `MINOR`: backward-compatible language enhancements
  - `PATCH`: bugfixes, diagnostic text improvements that don’t break stable ids

Include a `CHANGELOG.md` for released milestones.

---

## 13. Development Phases (Implementation Plan)

### Phase 1 — Language Design (no code first)
Deliver:
- domain model documentation
- MVP grammar + syntax examples
- diagnostic philosophy

Exit criteria:
- MVP syntax examples for:
  - valid program
  - undefined prerequisite
  - duplicate course code
  - cycle detection scenario

### Phase 2 — Grammar Implementation
Deliver:
- grammar definition (textX or alternative)
- parser that outputs AST with positions

Exit criteria:
- parser test suite passes for MVP programs

### Phase 3 — Semantic Analysis
Deliver:
- symbol table
- reference resolution
- prerequisite cycle detection

Exit criteria:
- errors reported with line/column + hints

### Phase 4 — Diagnostics Engine
Deliver:
- diagnostic structure + collector
- CLI formatting
- snapshot tests for diagnostics

Exit criteria:
- every semantic/validation error is diagnostic-based, not thrown as raw exceptions

### Phase 5 — IR Generator
Deliver:
- AST → IR transform
- stable ordering + versioned IR schema

Exit criteria:
- integration tests assert IR shape for valid DSL

### Phase 6 — Graph Engine
Deliver:
- build graph nodes/edges from IR
- topological ordering (or cycle handling)
- bottleneck analysis later (optional)

Exit criteria:
- graph outputs match expected edges and cycle info

### Phase 7 — Tooling + Release Candidate
Deliver:
- CLI usage docs
- developer docs
- test coverage improvement

Exit criteria:
- “compile → diagnostics → IR → graph” works end-to-end

---

## 14. CI/CL Checklist (Quality Gates)

At minimum:
- lint + format
- unit tests
- integration tests
- build/typecheck (if applicable)
- run a small compile on example DSL (smoke test)

---

## 15. What to Do Next (Actionable Start)

1. Decide the implementation split:
   - textX (Python) + TS (IR/graph) OR single language
2. Create the monorepo folders exactly as above
3. Implement only:
   - `program`, `semester`, `course`, `credits`, `requires`
4. Build the simplest compiler pipeline:
   - parse → AST
   - semantic: undefined prerequisites + duplicate codes
   - diagnostics with line/column
   - IR generation
   - graph edges
5. Add 5–10 test fixtures and keep extending.

---

## Appendix A — Example Diagnostic Requirements

Example error (required educational style):

> ERROR: Course CS201 references prerequisite CS999, which does not exist.  
> Hint: Did you mean CS101?  

Implementation requirement:
- message must be deterministic enough for snapshot testing
- line/column must point to the reference token location in the DSL

---

## Appendix B — Example Repository Config Files (Outline)

- `package.json` (root): workspace scripts
- `.github/workflows/ci.yml`: lint/test
- `pyproject.toml`: formatter/linter/test config for Python
- per-package:
  - `tsconfig.json` (if TS packages)
  - `package.json` (if TS packages)

(You’ll fill these based on whether you go hybrid or single language.)