# Workspace Rules: Elevo Internship

## Core Directive: Strictly Follow Internship Scope — No Over-Engineering

1. **Adhere to Task Specifications**:
   - For every task (Task 1 through Task 9), implement exactly what is described in the assignment context (`context/Python Programming & AI Tasks.pdf.pdf`).
   - Do not add extraneous layers, speculative enterprise patterns, or unwarranted architectural complexity.

2. **Keep Implementations Lean & Idiomatic**:
   - Favor simple, clean, readable Python code.
   - Keep file counts minimal: a single module/script (or runner + module when specified by the prompt), a concise unit test file, and a short README.
   - Avoid unnecessary class hierarchies or wrapper layers when simple functions or standard library features suffice.

3. **Standard Approval Workflow & Rigorous Verification Loop**:
   - **Step 1 - Plan Formulation & Double-Check**:
     - Review task requirements in the `context/` PDF.
     - Conduct a strict **two-pass review** of the plan against all listed objectives, constraints, and bonuses before submitting it to the user.
     - Present the concise, non-over-engineered plan for user review.
   - **Step 2 - User Approval**:
     - Wait for explicit user approval before executing in the respective `taskN/` directory (unless pre-authorized by the user).
   - **Step 3 - Execution**:
     - Implement cleanly and concisely according to the approved plan.
   - **Step 4 - Objective Review & Verification Loop**:
     - Re-read the task's exact section in the context PDF.
     - Cross-check every listed requirement, core constraint, and bonus item against the implementation.
     - Run the code and automated tests to verify full satisfaction of all objectives.
   - **Step 5 - Report & Next Task**:
     - Only when all requirements are fully satisfied, present the verification summary and ask for approval on the next task plan.
