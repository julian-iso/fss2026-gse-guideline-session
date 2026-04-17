# 🧪 GSE Guideline Session – Topic 04: Testing

**Team:** The Testing Team  
**Authors:** Julian Maurus, Sebastian Menzel, Simon Wally  
**Date:** 22 April 2026

---

## 👋 Welcome

This repository accompanies our **guideline session on software testing with LLMs**. It contains everything you need to follow along during our presentation, practice the example problems hands-on, and evaluate your own results.

The session is built around one central question:

> *Does following structured guidelines actually make you better at using LLMs for testing tasks?*

You'll find out for yourself.

---

## 📂 Repository Overview

| File / Folder | Description |
|---|---|
| `Topic-04_Guidelines.md` | Our testing guidelines — the core artifact of this session |
| `Topic-04_Example-Problems.md` | Three hands-on problems to practice with |
| `Topic-04_Evaluation.md` | Evaluation criteria and model solutions to assess your work |
| `problems/01_test-generation/` | Starter code + model solution for Problem 01 |
| `problems/02_test-validation/` | Starter test suite for Problem 02 |
| `problems/03_test-objective/` | Starter code for Problem 03 |

---

## 🗺️ How the Session Works

### Step 1 — Listen & Read

Follow our presentation. Afterwards (or in parallel), read through the guidelines:

📄 **[`Topic-04_Guidelines.md`](./Topic-04_Guidelines.md)**

These guidelines give you concrete, actionable rules for using LLMs to generate, validate, and contextualize software tests.

---

### Step 2 — Solve the Example Problems

Open **[`Topic-04_Example-Problems.md`](./Topic-04_Example-Problems.md)** and work through the three problems below. Each problem comes in **two rounds**:

#### 🔁 Round 1 — Without Guidelines
Attempt the problem using an LLM freely, without consulting our guidelines. Note down your approach, what prompts you used, and how long it took.

#### 🔁 Round 2 — With Guidelines
Repeat the same problem, but this time apply the relevant guidelines from `Topic-04_Guidelines.md`. Again note your approach and time.

---

### The Three Problems

#### Problem 01 · Test Generation ⏱ ~15 min

A friend built a **password validator** and wants you to stress-test it using an LLM. Your job is to generate tests that uncover edge cases and potential crashes.

> Starter code: [`problems/01_test-generation/validate_password.py`](./problems/01_test-generation/validate_password.py)

The validator enforces these rules:
- Length between **8 and 20** characters
- At least one **digit**
- At least one **uppercase** letter
- Must **not** contain the word `password` (case-insensitive)

---

#### Problem 02 · Test Validation ⏱ ~15 min

Your friend wrote his own pytest suite — but he was in a rush and suspects some tests are buggy or useless. Use an LLM to **review** the tests and flag the imposters.

> Starter tests: [`problems/02_test-validation/test_starter.py`](./problems/02_test-validation/test_starter.py)

Look out for: missing assertions, misleading test names, tests that always pass, and poor isolation.

---

#### Problem 03 · Test Objective ⏱ ~15 min

A `UserLogin` class introduces a subtle bug: the `login` method strips whitespace from the **input** before comparing it to the **stored** password (which may itself contain whitespace). Your task is to use an LLM to expose this flaw — and discover how much context you give the LLM matters.

> Starter code: [`problems/03_test-objective/user_login.py`](./problems/03_test-objective/user_login.py)

Try prompting the LLM with only the `validate_password` method first, then with the full class. Compare the results.

---

### Step 3 — Evaluate Your Results

Open **[`Topic-04_Evaluation.md`](./Topic-04_Evaluation.md)** and assess the solutions from both rounds.

For each problem you'll find:
- ✅ The **expected test cases** and correct outcomes
- ⚠️ **Common mistakes** to watch out for
- 🔗 Links to **model solutions**
- 📋 **Evaluation criteria** (assertion quality, coverage, edge-case robustness, readability, and more)

Ask yourself:
- Did applying the guidelines change your results?
- Which round produced better tests?
- Which round was faster?

---

## 🧭 Quick-Start Checklist

- [ ] Read through `Topic-04_Guidelines.md`
- [ ] Attempt **Problem 01** without guidelines → then with guidelines
- [ ] Attempt **Problem 02** without guidelines → then with guidelines
- [ ] Attempt **Problem 03** without guidelines → then with guidelines
- [ ] Use `Topic-04_Evaluation.md` to evaluate all six attempts
- [ ] Reflect: what difference did the guidelines make?

---

## 💡 Tips

- Keep your LLM prompts and responses somewhere you can compare them side by side.
- Don't skip Round 1 — the contrast is the whole point.
- For Problem 03, try giving the LLM progressively more context and observe how its output changes.

---

*Questions? Reach out to Julian, Sebastian, or Simon during the session.*