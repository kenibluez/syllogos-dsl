# Syllogos DSL — Syntax Specification v0.1

Version: 0.1
Status: Draft
Audience: Language engineers, curriculum designers, program directors

---

## 1. Overview

Syllogos is a human-readable DSL for defining, validating, and analyzing
university curricular maps. It is designed to be written by program directors
without programming experience, while remaining strict and machine-analyzable.

The language is **statement-based**: each statement declares or links an entity.
Statements are ordered but references may be forward or backward (the compiler
resolves all references after a full parse).

---

## 2. Design Principles

1. **Human-readable first**: reads like a curriculum editing script.
2. **Declarative**: you say *what* exists and *how things relate*, not *how to
   compute* them.
3. **Forgiving references**: courses and blocks can be referenced before they
   are declared (forward references are allowed).
4. **Statement-based**: one logical action per statement.
5. **Minimal punctuation**: no braces, no semicolons.
6. **Educational diagnostics**: every error includes a hint.

---

## 3. File Conventions

- File extension: `.syl`
- Encoding: UTF-8
- Line endings: LF or CRLF (normalized internally)
- Case sensitivity:
  - **Keywords are case-insensitive** (`CREATE`, `create`, and `Create` are all
    valid)
  - **Course codes are case-sensitive** (`CS101` ≠ `cs101`)
  - **Program and block names are case-insensitive for matching** but their
    original casing is preserved in output
- Comments: lines starting with `#` are ignored

Example comment:
```
# This is a comment
CREATE PROGRAM "Software Engineering"
```

---

## 4. Core Entities

| Entity    | Description                                              |
|-----------|----------------------------------------------------------|
| `PROGRAM` | Top-level container for a curricular map                 |
| `COURSE`  | A course in the catalog; may or may not be in any block  |
| `BLOCK`   | A time window (semester, quarter, month, etc.)           |

### Relationships

```
PROGRAM
  ├── COURSE (catalog member)
  │     └── PREREQUISITE → another COURSE
  └── BLOCK (optional)
        └── COURSE (placed reference)
```

---

## 5. Statements

### 5.1 CREATE PROGRAM

Declares a new program. Must appear before any other statement referencing
that program.

**Syntax:**
```
CREATE PROGRAM "<program-name>"
```

**Rules:**
- `<program-name>` is a quoted string.
- Program names must be unique within a file.
- A file may define more than one program.

**Example:**
```
CREATE PROGRAM "Software Engineering"
```

---

### 5.2 CREATE COURSE

Declares a new course. A course exists in the catalog regardless of whether
it is placed in a block.

**Syntax (full form):**
```
CREATE COURSE "<course-name>", <COURSE-CODE> WITH CREDITS <n>
IN PROGRAM "<program-name>"
```

**Syntax (short form — credits deferred):**
```
CREATE COURSE "<course-name>", <COURSE-CODE>
IN PROGRAM "<program-name>"
```

**Rules:**
- `<course-name>` is a quoted string.
- `<COURSE-CODE>` is an unquoted identifier: uppercase letters followed by
  digits (e.g. `CS101`, `MAT203`, `PY101`).
- `WITH CREDITS <n>` is optional in draft mode; required in strict mode.
- `<n>` must be a positive integer.
- Course codes must be unique within a program.
- `IN PROGRAM` is required.

**Examples:**
```
CREATE COURSE "Python Programming", PY101 WITH CREDITS 4
IN PROGRAM "Software Engineering"

CREATE COURSE "Java Programming", CS1020 WITH CREDITS 4
IN PROGRAM "Software Engineering"
```

**Draft mode (credits deferred):**
```
CREATE COURSE "Elective TBD", EL999
IN PROGRAM "Software Engineering"
```
→ Emits warning `SYL_WARN_MISSING_CREDITS`.

---

### 5.3 ADD PREREQUISITE

Declares that one course requires another as a prerequisite.
Prerequisites form the edges of the dependency graph.

**Syntax:**
```
ADD PREREQUISITE <COURSE-CODE> TO COURSE <COURSE-CODE>
```

**Rules:**
- Both course codes must be declared in the same program.
- A course may have multiple prerequisites (one `ADD PREREQUISITE` per
  prerequisite).
- Circular prerequisites are not allowed (detected and reported as errors).
- Forward references are allowed: you may add prerequisites before both
  courses are declared, as long as they are declared somewhere in the file.

**Example:**
```
ADD PREREQUISITE PY101 TO COURSE CS1020
```

This means: `CS1020` requires `PY101` before it can be taken.

**Multiple prerequisites:**
```
ADD PREREQUISITE PY101 TO COURSE CS1020
ADD PREREQUISITE MAT101 TO COURSE CS1020
```

---

### 5.4 CREATE BLOCK

Declares a time window (semester, quarter, 3-month period, etc.) inside a
program. Blocks are optional: a program may have courses with no blocks at
all.

**Syntax:**
```
CREATE BLOCK "<block-label>" IN PROGRAM "<program-name>"
```

**Rules:**
- `<block-label>` is a quoted string (flexible: `"Semester 1"`, `"Quarter 2"`,
  `"Freshman I"`, `"Month 3"`, etc.).
- Block labels must be unique within a program.
- Block order in the output is determined by order of appearance in the file.
- A program may have zero blocks.

**Example:**
```
CREATE BLOCK "Freshman I" IN PROGRAM "Software Engineering"
CREATE BLOCK "Sophomore I" IN PROGRAM "Software Engineering"
```

---

### 5.5 ADD COURSE TO BLOCK

Places a catalog course into a block (time window). This is the placement
statement: it says "this course is taught during this block."

**Syntax (by code):**
```
ADD COURSE <COURSE-CODE> TO BLOCK "<block-label>"
```

**Syntax (by name):**
```
ADD COURSE "<course-name>" TO BLOCK "<block-label>"
```

**Rules:**
- The course must be declared in the same program as the block.
- The block must be declared in the same program.
- A course may appear in at most one block per program (placing the same
  course in two blocks is an error).
- Name-based references are allowed as a convenience. If two courses share
  the same name, a code-based reference is required (compiler emits
  `SYL_ERR_AMBIGUOUS_COURSE_NAME`).
- Forward references are allowed.

**Examples:**
```
ADD COURSE PY101 TO BLOCK "Freshman I"
ADD COURSE CS1020 TO BLOCK "Sophomore I"

# By name (convenience):
ADD COURSE "Python Programming" TO BLOCK "Freshman I"
```

---

### 5.6 ADD COURSE TO PROGRAM (catalog-only placement)

Attaches a course to a program without placing it in any block. Useful when
a course exists in the catalog but is not yet scheduled.

**Syntax:**
```
ADD COURSE <COURSE-CODE> TO PROGRAM "<program-name>"
```

**Rules:**
- The course must already be declared with `CREATE COURSE`.
- If `CREATE COURSE ... IN PROGRAM ...` was already used, this statement is
  redundant but not an error (emits `SYL_INFO_ALREADY_IN_PROGRAM`).

**Example:**
```
CREATE COURSE "Java Programming", CS1020 WITH CREDITS 4
ADD COURSE CS1020 TO PROGRAM "Software Engineering"
```

---

## 6. Course Code Format

Course codes follow this pattern:

```
<PREFIX><NUMBER>
```

Where:
- `<PREFIX>`: one or more uppercase letters (e.g. `CS`, `MAT`, `PY`, `ENG`)
- `<NUMBER>`: one or more digits (e.g. `101`, `1020`, `203`)

Valid examples: `CS101`, `PY101`, `MAT203`, `CS1020`, `ENG01`
Invalid examples: `cs101` (lowercase), `101CS` (digits before letters),
`CS-101` (hyphens not allowed in v0.1)

---

## 7. Comments

Lines beginning with `#` are treated as comments and ignored by the compiler.
Inline comments (end-of-line `#`) are also supported.

```
# Define the program
CREATE PROGRAM "Software Engineering"  # main program
```

---

## 8. Full Example

This example reflects the scenario described in the design sessions:
- Two original courses (`Java Programming I` and `Java Programming II`) were
  retired.
- They were condensed into `Java Programming` (`CS1020`).
- A new prerequisite course `Python Programming` (`PY101`) was introduced.
- `PY101` goes into block `"Freshman I"` and `CS1020` into `"Sophomore I"`.

```
# Syllogos v0.1 example
# Program: Software Engineering

CREATE PROGRAM "Software Engineering"

# Course catalog

CREATE COURSE "Python Programming", PY101 WITH CREDITS 4
IN PROGRAM "Software Engineering"

CREATE COURSE "Java Programming", CS1020 WITH CREDITS 4
IN PROGRAM "Software Engineering"

# Prerequisites

ADD PREREQUISITE PY101 TO COURSE CS1020

# Curricular blocks (optional)

CREATE BLOCK "Freshman I" IN PROGRAM "Software Engineering"
CREATE BLOCK "Sophomore I" IN PROGRAM "Software Engineering"

# Block placements

ADD COURSE PY101 TO BLOCK "Freshman I"
ADD COURSE CS1020 TO BLOCK "Sophomore I"
```

---

## 9. Validation Rules (v0.1)

| Code                           | Severity | Description                                              |
|--------------------------------|----------|----------------------------------------------------------|
| `SYL_ERR_DUPLICATE_PROGRAM`    | error    | Two programs share the same name in the same file        |
| `SYL_ERR_DUPLICATE_COURSE`     | error    | Two courses share the same code in the same program      |
| `SYL_ERR_UNDEFINED_COURSE`     | error    | A course code referenced does not exist in the program   |
| `SYL_ERR_UNDEFINED_BLOCK`      | error    | A block label referenced does not exist in the program   |
| `SYL_ERR_UNDEFINED_PROGRAM`    | error    | A program name referenced does not exist in the file     |
| `SYL_ERR_CYCLE_DETECTED`       | error    | A cycle exists in the prerequisite graph                 |
| `SYL_ERR_COURSE_IN_TWO_BLOCKS` | error    | A course is placed in more than one block                |
| `SYL_ERR_AMBIGUOUS_COURSE_NAME`| error    | A name-based reference matches more than one course code |
| `SYL_ERR_INVALID_CREDITS`      | error    | Credits value is not a positive integer                  |
| `SYL_ERR_INVALID_COURSE_CODE`  | error    | Course code does not match the expected pattern          |
| `SYL_WARN_MISSING_CREDITS`     | warning  | A course is declared without credits (draft mode)        |
| `SYL_INFO_ALREADY_IN_PROGRAM`  | info     | A course is added to a program it already belongs to     |

---

## 10. Diagnostic Format

Every diagnostic includes:
- **severity**: `error`, `warning`, or `info`
- **code**: stable identifier (e.g. `SYL_ERR_UNDEFINED_COURSE`)
- **message**: human-readable description
- **line / column**: location in the source file
- **hint**: actionable suggestion (always present for errors and warnings)

**Example diagnostic output:**
```
ERROR [SYL_ERR_UNDEFINED_COURSE] Line 12, Col 18
  Course code CS999 is referenced but has not been declared in program
  "Software Engineering".
  Hint: Did you mean CS1020? Check your CREATE COURSE statements.
```

---

## 11. Reserved Keywords

The following words are reserved and may not be used as course names or
block labels (case-insensitive):

```
CREATE, PROGRAM, COURSE, BLOCK, ADD, TO, IN, WITH, CREDITS,
PREREQUISITE, REQUIRES
```

---

## 12. Multi-Program Files

A single `.syl` file may contain more than one program. Each program is
independent: course codes and block labels are unique per program, not
globally.

```
CREATE PROGRAM "Software Engineering"

CREATE COURSE "Python Programming", PY101 WITH CREDITS 4
IN PROGRAM "Software Engineering"

CREATE PROGRAM "Computer Science"

CREATE COURSE "Discrete Mathematics", MAT201 WITH CREDITS 3
IN PROGRAM "Computer Science"
```

Course codes may be reused across programs (they are scoped to their
program). Two programs may independently define `CS101` with different
names or credits.

---

## 13. Versioning

This document describes Syllogos DSL **v0.1**.

| Change type                              | Version bump |
|------------------------------------------|--------------|
| New statement forms or new keywords      | MINOR        |
| Changes to existing statement semantics  | MAJOR        |
| Diagnostic text / hint improvements      | PATCH        |
| New validation rules (non-breaking)      | MINOR        |

---

## 14. What Is Not in v0.1

The following features are explicitly deferred:

- Elective groups / course groups
- Co-requisites
- Max credits per block constraints
- Course modality (online, in-person, hybrid)
- Multiple prerequisites expressed inline (use multiple `ADD PREREQUISITE`
  statements)
- Import / include of external `.syl` files
- Aliases or short names for programs

These may be proposed for v0.2 and beyond.