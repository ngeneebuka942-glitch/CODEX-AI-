
from flask import Flask, request, jsonify, render_template
import ast
import re

app = Flask(__name__)

APP_NAME = "CODEX AI"
VERSION = "2.0.0"

SUPPORTED_LANGUAGES = [
    "Python", "JavaScript", "HTML", "CSS", "PHP",
    "Java", "C++", "TypeScript", "JSON", "Unknown"
]


def detect_language(code):
    text = code.strip()

    if not text:
        return "Unknown"

    if re.search(r"<!DOCTYPE html|<html|<head|<body", text, re.I):
        return "HTML"

    if re.search(r"<\?php", text):
        return "PHP"

    if re.search(r"^\s*(import |from |def |class |print\(|if __name__)", text, re.M):
        return "Python"

    if re.search(r"^\s*(interface |type .* =|const .*:\s*(string|number|boolean))", text, re.M):
        return "TypeScript"

    if re.search(r"^\s*(const |let |var |function |console\.log|=>)", text, re.M):
        return "JavaScript"

    if re.search(r"^\s*(public class |private class |System\.out\.println)", text, re.M):
        return "Java"

    if re.search(r"#include\s*<|using namespace std|int main\s*\(", text):
        return "C++"

    if re.search(r"[.#][\w-]+\s*\{[^}]*\}", text, re.S):
        return "CSS"

    if re.match(r"^\s*[\[{]", text):
        try:
            import json
            json.loads(text)
            return "JSON"
        except Exception:
            pass

    return "Unknown"


def python_errors(code):
    issues = []

    try:
        ast.parse(code)
    except SyntaxError as error:
        issues.append({
            "type": "Syntax Error",
            "line": error.lineno,
            "message": error.msg
        })

    return issues


def analyze_code(code, language):
    issues = []
    lines = code.splitlines()

    if not code.strip():
        return [{
            "type": "Empty Code",
            "line": 1,
            "message": "There is no code to analyze."
        }]

    if language == "Python":
        issues.extend(python_errors(code))

    patterns = [
        (r"\bTODO\b", "Pending Task", "This section still contains a TODO note."),
        (r"\bFIXME\b", "Pending Fix", "This section has been marked for fixing."),
        (r"\beval\s*\(", "Potential Risk", "eval() executes dynamically supplied code. Review its use."),
        (r"\bdebugger\s*;", "Debug Statement", "Remove debugger statements before production."),
        (r"console\.log\s*\(", "Debug Output", "Consider removing development console output.")
    ]

    for number, line in enumerate(lines, start=1):
        for pattern, issue_type, message in patterns:
            if re.search(pattern, line, re.I):
                issues.append({
                    "type": issue_type,
                    "line": number,
                    "message": message
                })

        if len(line) > 300:
            issues.append({
                "type": "Long Line",
                "line": number,
                "message": "This line is unusually long. Consider splitting it."
            })

    if len(lines) > 1000:
        issues.append({
            "type": "Large File",
            "line": 1,
            "message": "This file is large. Consider splitting it into smaller modules."
        })

    return issues


def explain_code(code, language):
    lines = code.splitlines()
    explanations = []

    explanations.append(f"Detected language: {language}")
    explanations.append(f"Total lines: {len(lines)}")
    explanations.append("")

    if language == "Python":
        explanations.append("PYTHON CODE BREAKDOWN")

        for number, line in enumerate(lines, start=1):
            clean = line.strip()

            if not clean:
                continue

            if clean.startswith("#"):
                meaning = "Comment: explains the code without being executed."
            elif clean.startswith(("import ", "from ")):
                meaning = "Imports an external module or selected functionality."
            elif clean.startswith("def "):
                meaning = "Defines a reusable function."
            elif clean.startswith("class "):
                meaning = "Defines a class or object blueprint."
            elif clean.startswith("if "):
                meaning = "Checks a condition before executing a block."
            elif clean.startswith("elif "):
                meaning = "Checks another condition if the previous condition was false."
            elif clean.startswith("else:"):
                meaning = "Runs when the previous conditions are not satisfied."
            elif clean.startswith("for "):
                meaning = "Repeats instructions for each item in a sequence."
            elif clean.startswith("while "):
                meaning = "Repeats instructions while a condition remains true."
            elif clean.startswith("return"):
                meaning = "Sends a value back from a function."
            elif clean.startswith("print("):
                meaning = "Displays information in the output."
            elif "=" in clean:
                meaning = "Assigns a value to a variable."
            else:
                meaning = "Executes an instruction or expression."

            explanations.append(f"Line {number}: {meaning}")
            explanations.append(f"  Code: {clean}")

    else:
        explanations.append("GENERAL CODE BREAKDOWN")

        for number, line in enumerate(lines, start=1):
            clean = line.strip()

            if not clean:
                continue

            if clean.startswith("//") or clean.startswith("#"):
                meaning = "Comment or developer note."
            elif "function " in clean or "def " in clean:
                meaning = "Declares a function."
            elif "class " in clean:
                meaning = "Declares a class."
            elif "import " in clean or "include " in clean:
                meaning = "Loads a module or external dependency."
            elif "if " in clean:
                meaning = "Introduces a conditional check."
            elif "for " in clean or "while " in clean:
                meaning = "Introduces a loop."
            elif "return" in clean:
                meaning = "Returns a value."
            elif "{" in clean or "}" in clean:
                meaning = "Defines or closes a code block."
            else:
                meaning = "Contains a statement or expression."

            explanations.append(f"Line {number}: {meaning}")
            explanations.append(f"  Code: {clean}")

    explanations.append("")
    explanations.append(
        "Note: This is a local static explanation, not a full execution of your program."
    )

    return "\n".join(explanations)


def optimize_code(code, language):
    suggestions = []

    if not code.strip():
        return ["Enter some code before requesting optimization."]

    lines = code.splitlines()

    if len(lines) > 100:
        suggestions.append(
            "Consider splitting this file into smaller functions or modules."
        )

    if language == "Python":
        suggestions.append("Use meaningful variable and function names.")
        suggestions.append("Consider adding docstrings to explain important functions.")
        suggestions.append("Avoid repeating the same logic in multiple places.")

        try:
            ast.parse(code)
            suggestions.append("Python syntax check passed.")
        except SyntaxError:
            suggestions.append("Fix Python syntax errors before optimizing.")

    elif language in ["JavaScript", "TypeScript"]:
        suggestions.append("Use const for variables that are never reassigned.")
        suggestions.append("Separate large functions into smaller reusable functions.")
        suggestions.append("Handle errors around operations that can fail.")
        suggestions.append("Remove unnecessary console.log statements before production.")

    elif language == "HTML":
        suggestions.append("Use semantic HTML elements where possible.")
        suggestions.append("Add accessible labels to form controls.")
        suggestions.append("Keep CSS and JavaScript in separate files for larger projects.")

    elif language == "CSS":
        suggestions.append("Group related selectors together.")
        suggestions.append("Use CSS variables for repeated colors and spacing.")
        suggestions.append("Remove unused selectors.")

    else:
        suggestions.append("Use consistent indentation and naming.")
        suggestions.append("Break complex logic into smaller reusable sections.")
        suggestions.append("Add useful comments to explain complex operations.")

    if any(len(line) > 300 for line in lines):
        suggestions.append("Break unusually long lines into smaller readable sections.")

    if re.search(r"\beval\s*\(", code):
        suggestions.append("Review eval() usage because it can introduce security risks.")

    return suggestions


def safe_correct(code, language):
    corrected = code
    changes = []

    cleaned = "\n".join(line.rstrip() for line in corrected.splitlines())

    if cleaned != corrected:
        corrected = cleaned
        changes.append("Removed trailing whitespace.")

    if corrected and not corrected.endswith("\n"):
        corrected += "\n"
        changes.append("Added a final newline.")

    if language == "Python":
        try:
            ast.parse(corrected)
            changes.append("Python syntax validation passed.")
        except SyntaxError as error:
            changes.append(
                f"Syntax issue remains on line {error.lineno}: {error.msg}. "
                "No automatic syntax rewrite was attempted."
            )

    if not changes:
        changes.append("No safe automatic changes were necessary.")

    return corrected, changes


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({
        "status": "online",
        "app": APP_NAME,
        "version": VERSION,
        "authentication": False,
        "mode": "local analysis"
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}

    code = data.get("code", "")
    action = data.get("action", "explain")

    if not isinstance(code, str):
        return jsonify({
            "success": False,
            "error": "Code must be text."
        }), 400

    if len(code) > 200000:
        return jsonify({
            "success": False,
            "error": "Code is too large. Maximum size is 200 KB."
        }), 413

    language = detect_language(code)

    if action == "explain":
        result = explain_code(code, language)

        return jsonify({
            "success": True,
            "action": action,
            "language": language,
            "result": result
        })

    elif action == "errors":
        issues = analyze_code(code, language)

        result = "\n".join(
            f"[{item['type']}] Line {item['line']}: {item['message']}"
            for item in issues
        )

        if not result:
            result = "No issues found by the available local checks."

        return jsonify({
            "success": True,
            "action": action,
            "language": language,
            "issues": issues,
            "result": result
        })

    elif action == "optimize":
        suggestions = optimize_code(code, language)

        result = "\n".join(
            f"{number}. {item}"
            for number, item in enumerate(suggestions, start=1)
        )

        return jsonify({
            "success": True,
            "action": action,
            "language": language,
            "suggestions": suggestions,
            "result": result
        })

    elif action in ["fix", "correct"]:
        corrected, changes = safe_correct(code, language)

        return jsonify({
            "success": True,
            "action": "fix",
            "language": language,
            "corrected_code": corrected,
            "changes": changes,
            "result": "\n".join(changes)
        })

    else:
        return jsonify({
            "success": False,
            "error": "Unknown action. Use explain, errors, optimize, or fix."
        }), 400


if __name__ == "__main__":
    print("--------------------------------")
    print("       CODEX AI SERVER")
    print("--------------------------------")
    print(f"Version: {VERSION}")
    print("Status: Starting...")
    print("Authentication: Disabled")
    print("Local analysis: Enabled")
    print("Address: http://127.0.0.1:5000")
    print("--------------------------------")

    app.run(host="127.0.0.1", port=5000, debug=False)
