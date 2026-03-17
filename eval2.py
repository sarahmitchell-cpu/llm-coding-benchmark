#!/usr/bin/env python3
"""
Evaluation script for harder coding tasks - Round 2.
Tests redesigned tasks 007, 008 (with retry), 009 (new bug), 010 (new bug).
"""

import os, sys, json, shutil, subprocess, tempfile, re, time
import requests

API_KEY = "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"
TASKS_DIR = "/tmp/harder-tasks"

TASKS = [
    "007_lichao_tree",
    "008_persistent_segtree",
    "009_suffix_array",
    "010_segtree_beats",
]

TASK_DESCRIPTIONS = {
    "007_lichao_tree": "Li Chao segment tree for minimum linear function queries over integer points",
    "008_persistent_segtree": "Persistent segment tree for k-th smallest element in a range",
    "009_suffix_array": "Suffix array construction with LCP array (O(n log n) doubling algorithm)",
    "010_segtree_beats": "Segment Tree Beats supporting range chmin, range sum query, range max query",
}

MODEL = "z-ai/glm-5"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

PROMPT_TEMPLATE = """You are an expert competitive programmer. The following Python code has one or more subtle bugs.

Task: {description}

Your job is to find and fix ALL bugs in the code so that it passes all test cases.
Return ONLY the corrected Python code with NO explanation, NO markdown fences, NO extra text.
The output must be runnable Python that can be saved directly to a .py file.

Buggy code:
{code}"""


def call_model(model, description, code, max_retries=3):
    prompt = PROMPT_TEMPLATE.format(description=description, code=code)
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 4096,
    }
    last_err = "unknown"
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=HEADERS,
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            raw = resp.json()
            content = raw["choices"][0]["message"]["content"]
            if content is None:
                last_err = f"null content (attempt {attempt+1})"
                print(f"  [attempt {attempt+1}] null response, retrying...")
                time.sleep(3)
                continue
            content = content.strip()
            if content.startswith("```"):
                lines = content.split("\n")
                lines = [l for l in lines if not l.strip().startswith("```")]
                content = "\n".join(lines).strip()
            return content
        except Exception as e:
            last_err = str(e)
            print(f"  [attempt {attempt+1}] exception: {e}, retrying...")
            time.sleep(3)
    return None, last_err


def run_tests(task_dir, solution_code):
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copy(os.path.join(task_dir, "test_solution.py"),
                    os.path.join(tmpdir, "test_solution.py"))
        with open(os.path.join(tmpdir, "solution.py"), "w") as f:
            f.write(solution_code)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test_solution.py", "-v",
             "--tb=short", "-q"],
            capture_output=True, text=True, cwd=tmpdir, timeout=30
        )
        output = result.stdout + result.stderr
        m = re.search(r"(\d+) passed", output)
        n_passed = int(m.group(1)) if m else 0
        m = re.search(r"(\d+) failed", output)
        n_failed = int(m.group(1)) if m else 0
        return result.returncode == 0, n_passed, n_failed, output


def run_baseline(task_dir):
    starter_path = os.path.join(task_dir, "starter.py")
    with open(starter_path) as f:
        code = f.read()
    ok, passed, failed, out = run_tests(task_dir, code)
    return ok, passed, failed


print("=" * 60)
print("Harder Coding Tasks - Round 2 Evaluation")
print(f"Model: {MODEL}")
print("=" * 60)

results = {}
for task in TASKS:
    task_dir = os.path.join(TASKS_DIR, task)
    desc = TASK_DESCRIPTIONS[task]

    print(f"\n{'='*60}")
    print(f"Task: {task}")
    print(f"{'='*60}")

    ok, passed, failed = run_baseline(task_dir)
    print(f"  [baseline] exit={'ok' if ok else 'fail'} passed={passed} failed={failed}")

    with open(os.path.join(task_dir, "starter.py")) as f:
        starter_code = f.read()

    print(f"  [{MODEL}] Calling {MODEL}...")
    result = call_model(MODEL, desc, starter_code)

    if isinstance(result, tuple):
        err = result[1]
        print(f"  [{MODEL}] EXCEPTION: {err}")
        results[task] = {"status": "ERROR", "passed": 0, "failed": 0, "note": err}
    elif result is None:
        print(f"  [{MODEL}] NULL after retries")
        results[task] = {"status": "ERROR", "passed": 0, "failed": 0, "note": "null after retries"}
    else:
        print(f"  [{MODEL}] Got {len(result)} chars. Running tests...")
        ok, passed, failed, out = run_tests(task_dir, result)
        status = "PASS" if ok else "FAIL"
        print(f"  [{MODEL}] {status} | passed={passed} failed={failed}")
        snippet = "\n".join(out.split("\n")[:20])
        print(f"  Output snippet:\n{snippet}\n")
        results[task] = {"status": status, "passed": passed, "failed": failed}

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
for task, r in results.items():
    status = r["status"]
    print(f"\n{task}:")
    print(f"  {MODEL:20s}: {status} (passed={r['passed']}, failed={r['failed']})")
