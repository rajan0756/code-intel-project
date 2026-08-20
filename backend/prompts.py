"""
Prompt templates for AI-Driven Code Intelligence & Automated Documentation System.

Each function takes the raw code (and optional filename/context) and returns
a prompt string ready to send to IBM Bob (or any LLM endpoint).
"""

def explanation_prompt(code: str, filename: str = "code.py") -> str:
    return f"""You are a senior software engineer explaining code to a new team member.

File: {filename}

Explain what this code does in plain English. Structure your answer as:
1. **Overview** (1-2 sentences: what is the overall purpose of this file?)
2. **Key components** (bullet list of the main functions/classes and what each does)
3. **How it fits together** (brief description of the flow/logic)

Avoid restating the code line-by-line. Focus on intent and behavior, not syntax.

Code:
```
{code}
```
"""


def diagram_prompt(code: str, filename: str = "code.py") -> str:
    return f"""You are a software architect. Produce a Mermaid.js flowchart for the code below.

Strict rules — violations will break the renderer:
- Output ONLY the Mermaid diagram. No explanation, no code fences, no comments.
- Always use `flowchart TD` as the first line.
- Show only the top-level functions/classes as nodes and arrows between them.
- Maximum 12 nodes total. If there are more, group minor helpers into one node called Helpers.
- Node labels: plain words only, NO quotes, NO special characters, NO punctuation.
  Good:  A[call ai]   Bad: A[call_ai("prompt")]
- Use only these node shapes: [rectangle] and {{diamond}} for decisions.
- NO subgraphs. NO classDiagram. NO styling lines.

File: {filename}

Code:
```
{code}
```
"""


def docs_prompt(code: str, filename: str = "code.py") -> str:
    return f"""You are a technical writer generating API documentation.

For each public function/class/method in the code below, produce a documentation
entry in this format:

### `function_name(params)`
**Description:** what it does
**Parameters:** name (type) - description, for each param
**Returns:** type - description
**Example:**
```
usage example here
```

Only document public/exported functions and classes (skip private helpers prefixed with `_`
unless the file has very few functions overall).

File: {filename}

Code:
```
{code}
```
"""
