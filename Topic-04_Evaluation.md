# Topic-04_Evaluation.md

## Team Information

**Team Name:** The Testing Team  
**Topic:** Testing  
**Date:** 22.04.2026  
**Authors:** Julian Maurus, Sebastian Menzel, Simon Wally  


## 1. Evaluation Criteria

### General Evaluation Criteria

* **Assertion Quality**: Do tests make precise assertions rather than vague checks (e.g., just asserting not null)?

* **Requirement Coverage:** Do the tests cover every stated rule/requirement, including positive and negative paths? (developers may also use tools like JaCoCo)

* **Determinism & Reliability:** Are tests stable and repeatable (no flaky behavior, random outcomes, or hidden environment dependencies)?

* **Readability & Maintainability:** Are test names descriptive, structure clear, duplication minimized (e.g., using parametrization where appropriate)?

* **Test Independence & Isolation:** Can each test run independently without shared state or reliance on execution order?

* **Fault Localization:** When a test fails, is it obvious which rule failed (avoid over-combining many failure causes in one test)?

* **Edge-Case Robustness:** Are unusual or risky inputs tested (e.g., None, wrong types, whitespace, mixed-case banned words)?

* **Boundary & Equivalence Design:** Are boundary values and representative input classes tested (e.g., min/max, just-below/just-above, valid/invalid categories)?

* **Guideline Adherence:** Does the solution follow the guidelines from [`Topic-04_Guidelines.md`](./Topic-04_Guidelines.md)?

## 2. Evaluation Specifically for Example Problems

### Problem 01: Test Generation

**Evaluation Description:**  
Ideally, a strong solution meets all defined evaluation criteria. However, for this specific task, special emphasis should be placed on **edge-case robustness** and **boundary/equivalence checks**, since these are the most common sources of missed defects in password-validation testing.

**Test Cases:**  
- **Test Case 1:** "Abcdefg1" → True
- **Test Case 2:** "lowercase1" → False
- **Test Case 3 (Edge Case):** None → TypeError
- **Test Case 4 (Edge Case):** "Abc 1234" → True
- **Test Case 5 (Edge Case):** "A1bcdefghijklmnopqrst" → False

**Correct Solution Code:**  
You can find the solution [here](./problems/01_test-generation/test_solution.py).

**Common Mistakes to Avoid:**  
- **No Invalid-Type Coverage:** Skipping inputs like None or numbers and not verifying whether the function returns False or raises an error.
- **Multi-Failure Tests:** Combining many failing conditions in one test, making it unclear which rule is being validated.  
- **Missing Boundaries:** Only testing a 10-character password and forgetting to test exactly 8 and 20 characters.  

---

### Problem 02: Test Validation

**Evaluation Description:**  
The main goal is to correctly distinguish meaningful tests from **misleading or ineffective** ones. A strong solution should identify weak assertions, missing assertions, and misleading test names, then suggest precise improvements.

**Test Cases:**  
- **Test Case 1:** Review `test_missing_uppercase` and `test_password_length_check` → **Expected Output:** Both are flagged as invalid/useless (no meaningful assertion of expected behavior).
- **Test Case 2:** Review `test_password_boundary` → **Expected Output:** The test is identified as only partially valid: it checks one valid-length example but does not actually cover boundaries.
- **Test Case 3:** Review `test_password_no_digit` → **Expected Output:** The test is identified as invalid because it fails for the wrong reason: the input is too short, so the test does not isolate the "missing digit" requirement.
- **Test Case 4 (Edge Case):** Review `test_password_exception_handling` → **Expected Output:** Flagged as unreliable because the try/except structure can pass without actually validating failure behavior.
- **Test Case 5 (Edge Case):** Review `test_password_valid` → **Expected Output:** Flagged as unreliable as the test only returns the output of the function and doesn't compare it to an assertion.

**Correct Solution Code:**  
  No separate code needed.

**Common Mistakes to Avoid:**  
- **Ignoring Assertion Quality:** Accepting tests with `assert True` or missing assertions as valid.
- **Focusing Only on Results:** Not checking whether test names and structure actually match what is being verified.

---

### Problem 03: Test Objective

**Evaluation Description:**  
In this problem, the key objective is to identify the login flaw introduced by applying `strip()` before password comparison. A strong solution should demonstrate that conclusions can differ significantly depending on whether the LLM is given only the `validate_password` method or the full class contex

**Test Cases:**  
- **Test Case 1:** `UserLogin("user", "Abcd1234").login("Abcd1234")` → **Expected Output:** `"✅ Login Successful!"`

- **Test Case 2:** `UserLogin("user", "Abcd1234 ").login("Abcd1234 ")` → **Expected Output:** `"❌ Login Failed!"` (reveals inconsistent behavior because the stored password keeps trailing whitespace, but input is stripped before comparison).

**Correct Solution Code:**  
  No separate code needed.

**Common Mistakes to Avoid:**  
- **Providing Too Little Context:** Sharing only `validate_password` or only login with the LLM, so the `strip()` side effect in the full class is missed.


## 3. References

All solutions in this document are directly derived from our proposed guidelines. For full details, see [`Topic-04_Guidelines.md`](./Topic-04_Guidelines.md).

---

*Template version: 1.0 | Last updated: 24 February 2026*
