# Topic-04_Example-Problems.md

## Team Information

**Team Name:** The Testing Team  
**Topic:** Testing  
**Date:** 22.04.2026  
**Authors:** Julian Maurus, Sebastian Menzel, Simon Wally  

## 1. Example Problems

### Problem 01: Test Generation

**Task Description:**  
A friend of yours is building a new app and just finished the password validation logic. He’s a great developer but admits he isn’t very experienced in "breaking" code or finding edge cases. He’s worried that a user might bypass his rules or that the app might crash if someone enters something unexpected.

He asks you for your help. Use an LLM to analyze his algorithm and generate tests that attempt to bypass the validation or trigger errors.  

**Prerequisites:**  
This problem requires PyTest. Install it using: `pip install pytest`

**Starter Artefacts:**  
You can find the artifacts [here](./problems/01_test-generation/validate_password.py).

**Guidelines to Apply:**  
- **Guideline 01:** Clarify what aspects of password validation need testing (boundary cases, error handling, etc.)
- **Guideline 02:** Structure your prompt with role, context, constraints and expected output format
- **Guideline 05:** Manually review the generated tests for accuracy, readability and alignment with best practices

**Time Estimate:** approx. 15 min

---

### Problem 02: Test Validation

**Task Description:**  
Your friend is grateful for your help! He has now written his own suite of pytest cases to feel more confident. However, he was in a rush and thinks some of his tests might be "buggy" or useless.

Your task is to use an LLM to perform a review of his tests and identify the imposters.

**Prerequisites:**  
This problem requires PyTest. Install it using: `pip install pytest`

**Starter Artefacts:**  
You can find the artifacts [here](./problems/02_test-validation/test_starter.py).

**Guidelines to Apply:**  
- **Guideline 03:** Validate the test cases, identify gaps or failures and iteratively refine based on results
- **Guideline 05:** Manually review the LLM's analysis for accuracy and alignment with testing best practices

**Time Estimate:** approx. 15 min

---

### Problem 03: Test Objective

**Task Description:**  
Your friend implemented a `UserLogin` class with password validation and login behavior. At first glance, everything looks correct.

Use an LLM in two phases:
1. Analyze only the `validate_password` method and describe which inputs should be accepted or rejected.
2. Analyze the full class and identify whether login behavior is fully consistent with that method-level analysis.

Finally, compare the LLM outputs from both phases and explain why the conclusions differ.

**Prerequisites:**  
None

**Starter Artefacts:**  
You can find the artifacts [here](./problems/03_test-objective/user_login.py).

**Guidelines to Apply:**  
- **Guideline 01:** Understand how scope and context affect what tests are considered necessary and sufficient
- **Guideline 05:** Manually review and validate the LLM's analysis to ensure it correctly identifies inconsistencies

**Time Estimate:** approx. 15 min


## 2. Instructions for Classmates (hands-on)

**How to Use These Problems:**

1. **Baseline Attempt:** Try solving the problem without using any guidelines first. Record your approach and time.
2. **Guideline-Driven Attempt:** Now apply the guidelines from the corresponding [`Topic-04_Guidelines.md`](./Topic-04_Guidelines.md) file. Record your approach and time.
3. **Compare:** Which approach was faster? Which produced better results? Document your observations.
4. **Evaluation:** Use the [`Topic-04_Evaluation.md`](./Topic-04_Evaluation.md) file to assess your solutions.

---

## 3. References

All problems in this document are directly derived from our proposed guidelines. For full details, see [`Topic-04_Guidelines.md`](./Topic-04_Guidelines.md).

---

*Template version: 1.0 | Last updated: 24 February 2026*
