# GEMINI.md - Autonomous Execution & Operational Rules

## 1. Pre-Granted Authorization & Autonomous Execution
- **Full Autonomous Authorization:** The user has explicitly pre-authorized all operations required to build, maintain, test, harden, and verify the `HOMEOPATHY_AGENT` project.
- **Do Not Ask Permission to Continue:** Never pause or halt execution to ask for user permission, confirmation, or approval to proceed to the next step, phase, or milestone.
- **Continuous Pipeline Progression:** When assigned a task, phase, or multi-step roadmap, execute sequentially and continuously through completion, running automated tests and reporting results.
- **No Halting Prompt Endings:** Do not conclude turns with questions such as:
  - "Whenever you are ready, confirm to proceed..."
  - "Shall I proceed to Phase X?"
  - "Please confirm to continue."
  - "Do you want me to execute this plan?"
  Instead, immediately proceed with execution and report verified outcomes.

## 2. Planning Mode & Artifact Protocol
- **Non-Blocking Artifacts:** Never set `RequestFeedback: true` on plan artifacts unless the user explicitly requests an interactive design pause.
- **No Circular Oscillation:** Strictly prohibit "wheel-spinning", repetitive re-auditing of already completed phases, or re-soliciting approval for locked architectures.
- **Zero Hallucination / Zero Guesswork:** Maintain absolute technical rigor, mathematical precision, and clinical safety standards across all implementations.
