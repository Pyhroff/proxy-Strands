# Proxy — Final Hackathon Demo Script

Target length: 3–4 minutes. Keep the live split-screen visible during the agent run.

## 0:00–0:20 — The problem

“Important online forms are difficult to complete, especially when users must navigate unfamiliar pages or provide sensitive information. An AI agent can help, but it must remain understandable, interruptible, and safe when the page itself is untrusted.”

## 0:20–0:45 — The product

“This is Proxy, a human-first browser agent. The left side explains each decision. The right side shows the actual live webpage. Proxy perceives the current page, reasons about one action, applies safety checks, and repeats.”

## 0:45–1:05 — Session setup

Open `http://127.0.0.1:8000/app/session.html`.

“Before a task starts, Proxy creates a temporary session. I provide ordinary profile details once. Sensitive values such as date of birth and SSN are deliberately not collected here.”

Click **Save profile** and continue to the split-screen.

## 1:05–2:15 — Clean application

Select **Normal application**, leave the task as **Complete the housing benefits application**, and click **Send**.

“Proxy is now reading the live form and making fresh decisions step by step, not replaying a fixed script.”

When DOB or SSN appears:

“This is the privacy boundary. Proxy pauses and asks me to enter the sensitive value directly. The value goes into the browser and is not supplied to the reasoning model.”

Enter the demo value and click **Done — Continue**.

When the approval prompt appears:

“Even after the form is complete, Proxy does not submit automatically. Final submission requires explicit human approval.”

Click **Approve**.

“The live page now shows the completed application state. The agent has finished under human control.”

## 2:15–3:05 — Attack demo

Run a new task with **Attack demo** selected.

“This page looks like the same form, but it contains hidden instructions designed to manipulate an AI agent.”

Wait for the red security event.

“Proxy stopped before acting. It treated the page as untrusted content instead of obeying it. This is defense in depth: page-content scanning, constrained browser actions, and human approval for irreversible actions.”

## 3:05–3:35 — Technical close

“The critical path is perceive, reason, gate, execute, and repeat. Sensitive input stays human-controlled, the browser view is observable, the agent can be interrupted, and final submission is never silent.”

“Proxy is not trying to remove people from important workflows. It removes repetitive work while keeping the person in control of the moments that matter.”

## Recording checklist

- Start the backend first:

  ```bat
  .\.venv\Scripts\python.exe -m uvicorn proxy.backend.main:app --host 127.0.0.1 --port 8000
  ```

- Open `http://127.0.0.1:8000/app/session.html`.
- Use demo values only; never record real SSNs or dates of birth.
- Do one clean run and one attack run before recording.
- Keep the approval prompt and blocked attack result on screen for 2–3 seconds.
- End on the split-screen success/block state, then show the GitHub URL.
