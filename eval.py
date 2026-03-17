#!/usr/bin/env python3
"""
Evaluation script for harder coding tasks.
Sends each starter.py to GLM-5 via OpenRouter, asks it to fix the bugs,
then runs the test suite against the model's output.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
import requests

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
TASKS_DIR = os.path.dirname(os.path.abspath(__file__))

TASKS = [
    "006_affine_segtree",
    "007_lichao_tree",
    "008_persistent_segtree",
    "009_suffix_array",
    "010_segtree_beats",
]

TASK_DESCRIPTIONS = {
    "006_affine_segtree": "Range affine segment tree (range multiply+add, range sum)",
    "007_lichao_tree": "Li Chao segment tree for minimum linear function queries",
    "008_persistent_segtree": "Persistent segment tree for k-th smallest in range",
    "009_suffix_array": "Suffix array construction with LCP array (O(n log n))",
    "010_segtree_beats": "Segment Tree Beats (range chmin + range sum/max)",
}

MODEL = "z-ai/glm-5"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

PROMPT_TEMPLATE = """You are an expert competitive programmer. The following Python code has one or more subtle bugs.

Task: {description}

Your job is to fix ALL bugs in the code so that it passes all test cases.
Return ONLY the corrected Python code, with no explanation, no markdown fences, no extra text.
The output must be valid Python that can be saved directly to a .py file and imported.

Buggy code:
{code}"""


def call_model(model, description, code):
    prompt = PROMPT_TEMPLATE.format(description=description, code=code)
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4096,
    }
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=HEADERS,
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            content = "\n".join(lines).strip()
        return content
    except Exception as e:
        return None, str(e)


def run_tests(task_dir, solution_code):
    """Write solution code to a temp dir and run pytest."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy test file
        shutil.copy(os.path.join(task_dir, "test_solution.py"),
                    os.path.join(tmpdir, "test_solution.py"))
        # Write the model's solution
        with open(os.path.join(tmpdir, "solution.py"), "w") as f:
            f.write(solution_code)
        # Run pytest
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test_solution.py", "-v",
             "--tb=short", "-q"],
            capture_output=True, text=True, cwd=tmpdir, timeout=30
        )
        output = result.stdout + result.stderr
        passed = output.count(" passed")
        failed = output.count(" failed")
        error = output.count(" error")
        # Extract counts
        import re
        m = re.search(r"(\d+) passed", output)
        n_passed = int(m.group(1)) if m else 0
        m = re.search(r"(\d+) failed", output)
        n_failed = int(m.group(1)) if m else 0
        return result.returncode == 0, n_passed, n_failed, output


def run_baseline(task_dir):
    """Check that the starter (buggy) code fails tests."""
    starter_path = os.path.join(task_dir, "starter.py")
    with open(starter_path) as f:
        code = f.read()
    ok, passed, failed, out = run_tests(task_dir, code)
    return ok, passed, failed


print("=" * 60)
print("Harder Coding Tasks - Model Evaluation")
print(f"Model: {MODEL}")
print("=" * 60)

results = {}

for task in TASKS:
    print(f"\n{'=' * 60}")
    print(f"Task: {task}")
    print("=" * 60)

    task_dir = os.path.join(TASKS_DIR, task)
    starter_path = os.path.join(task_dir, "starter.py")
    description = TASK_DESCRIPTIONS[task]

    with open(starter_path) as f:
        starter_code = f.read()

    # Baseline: verify buggy code fails
    print(f"  [baseline] Testing original buggy code...")
    base_ok, base_passed, base_failed = run_baseline(task_dir)
    print(f"  [baseline] exit={'0' if base_ok else '1'} passed={base_passed} failed={base_failed}")

    # Test GLM-5
    print(f"\n  [{MODEL}] Calling {MODEL}...")
    fixed_code = call_model(MODEL, description, starter_code)

    if fixed_code is None or isinstance(fixed_code, tuple):
        err = fixed_code[1] if isinstance(fixed_code, tuple) else "unknown"
        print(f"  [{MODEL}] EXCEPTION: {err}")
        results[task] = {"model": MODEL, "status": "ERROR", "passed": 0, "failed": 0}
        continue

    print(f"  [{MODEL}] Got {len(fixed_code)} chars. Running tests...")
    ok, passed, failed, output = run_tests(task_dir, fixed_code)

    status = "PASS" if ok else "FAIL"
    print(f"  [{MODEL}] {status} | passed={passed} failed={failed}")

    # Show last few lines of output
    lines = output.strip().split("\n")
    snippet = "\n".join(lines[-8:])
    print(f"  Output snippet:\n{snippet}\n")

    results[task] = {
        "model": MODEL,
        "status": status,
        "passed": passed,
        "failed": failed,
    }

# Summary
print("\n")
print("=" * 60)
print("SUMMARY")
print("=" * 60)
for task in TASKS:
    r = results.get(task, {})
    status = r.get("status", "?")
    passed = r.get("passed", "?")
    failed = r.get("failed", "?")
    print(f"\n{task}:")
    print(f"  {MODEL:<20}: {status} (passed={passed}, failed={failed})")
