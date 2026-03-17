# LLM Coding Benchmark: Advanced Data Structures

A benchmark for evaluating LLM code-repair capabilities on **hard algorithmic tasks** involving advanced data structures. The goal: find tasks where **GLM-5 fails** but **Claude succeeds**.

## 🎯 Task Design Philosophy

Each task contains a **subtly buggy implementation** of a classic algorithm. The model must:
1. Identify the bug(s)
2. Produce a correct implementation
3. Pass all provided test cases

Tasks are rated **"hard"** when:
- Bugs are subtle (off-by-one in invariants, asymmetric case handling, wrong termination conditions)
- The code structure looks plausible and compilable
- Standard LLM pattern-matching won't find the bug

## 📋 Tasks

| Task | Algorithm | Bug Type |
|------|-----------|----------|
| 006 | Affine Segment Tree | Wrong lazy composition order |
| 007 | Li Chao Tree | Incorrect line dominance check |
| 008 | Persistent Segment Tree | Wrong node aliasing in update |
| 009 | Suffix Array (SA-IS) | Wrong termination condition |
| 010 | Segment Tree Beats (Ji Driver) | Asymmetric cnt_max update |

## 🚀 Quick Start

```bash
pip install pytest requests
export OPENROUTER_API_KEY="your_key_here"
python eval.py
```

## 📊 Evaluation Results

### GLM-5 (z-ai/glm-5)
| Task | Result | Notes |
|------|--------|-------|
| 006 Affine SegTree | ❌ FAIL | Truncated output / syntax error |
| 007 Li Chao Tree | ❌ ERROR | Empty API response |
| 008 Persistent SegTree | ❌ ERROR | Empty API response |
| 009 Suffix Array | ❌ FAIL | Wrong on stress tests |
| 010 SegTree Beats | ❌ FAIL | Wrong on equal-max cases |

### Claude (Anthropic)
All 5 tasks: ✅ PASS

## 🔧 How It Works

1. Load buggy `starter.py` for each task
2. Send to model: "Fix the bugs in this code so all tests pass"
3. Extract Python code from model response
4. Run `pytest test_solution.py`
5. Record pass/fail

## License

MIT
