# manual_audit — web-agent kit for v0.3.1 pressure scenarios

Adapter-free way to run the three new (v0.3.1) form-check pressure scenarios
against ChatGPT, Gemini, Claude Web, or any chat-only model interface that
does not expose a programmatic API.

This kit was built because the Anthropic API path is not available right now,
but the same three scenarios still need empirical validation: do real-world
deployed models pass them, and does loading form-check change anything?

## What this measures (and what it does NOT)

Pass/fail per scenario per model per condition. That is it. Specifically:

- **MEASURES:** whether a given model, in a given condition (baseline =
  no form-check; treatment = form-check loaded via IDE-simulating preamble),
  produced a response that matches the scenario's pass_criteria.py.
- **DOES NOT MEASURE:** statistical pass-rate over many samples (web UI is
  single-shot, no temperature control). Numeric per-component subscores. The
  effect of any system prompt the web UI is injecting that you cannot see.
- **DOES NOT CALIBRATE:** rubric thresholds. Threshold calibration needs
  N>=50 and is gated separately.

## File layout

```
manual_audit/
  README.md                this file
  _preamble.txt            WINDSURF_SIM_PREAMBLE, byte-equal to the API harness
  bundles/
    01_red-flag_upstream-constraint-missed/
      baseline.txt         scenario setup + prompt (no form-check)
      treatment.txt        preamble + form-check SKILL.md + setup + prompt
    02_test-as-spec_test-locks-in-bug/
      baseline.txt
      treatment.txt
    03_hallucination_library-behavior-unverified/
      baseline.txt
      treatment.txt
  manual_audit.sh          wrapper: response file in, PASS/FAIL out, JSONL appended
  runs/
    results.jsonl          one line per trial; created on first wrapper run
```

## Procedure

For each scenario (3) x each model (your choice; suggest GPT-5, Gemini 2.5
Pro, Claude Web) x each condition (2 = baseline, treatment), do:

1. Open the appropriate `bundles/<shortname>/<condition>.txt` in a viewer.
2. Copy everything between `=== BEGIN_PASTE ===` and `=== END_PASTE ===`.
   Do NOT include the header lines starting with `#` or the BEGIN/END
   markers themselves.
3. Open a fresh chat in the target web UI. Disable any custom-instruction
   profile that might interfere (ChatGPT: temporary chat; Gemini: incognito
   conversation; Claude: new chat with no project context).
4. Paste the bundle content as one user message. Send.
5. Wait for the response to complete.
6. Copy the response text into a file. Suggested naming:
   `runs/<model>/<shortname>/<condition>.txt`
7. Run the wrapper:

   ```
   bash manual_audit.sh <shortname> <model> <condition> <response_file>
   ```

   Example:

   ```
   bash manual_audit.sh 01_red-flag_upstream-constraint-missed gpt-5-web \
     baseline runs/gpt-5/01_red-flag/baseline.txt
   ```

The wrapper appends one line to `runs/results.jsonl` with `ts`, `scenario`,
`model`, `condition`, `verdict`, `response`. Aggregate yourself.

## What "PASS" means

Each scenario's pass_criteria.py looks for specific marker phrases that
the reference response demonstrates. PASS does NOT mean the model gave the
ideal response, only that the response contained the load-bearing markers.
FAIL means the response missed at least one marker; read the response and
the pass_criteria.py to see which.

For diagnostic depth, also open the reference_response.md alongside the
model's response and note qualitative gaps (did it cite the right
primary source? did it suggest the right next action?).

## Divergence from the API harness

The API harness (harness_adapters/anthropic_opus.py) sends prompt.md alone
as the user message and puts SKILL.md in the system slot. This manual kit
sends setup.md + prompt.md combined as a single user message, because
web UIs do not expose a separate system slot and because prompt.md alone
is too thin to elicit a scenario-aware response.

For the treatment condition, the SKILL.md content is prepended via the
WINDSURF_SIM_PREAMBLE that the API harness uses, so the "skill is loaded"
framing is byte-equal.

## Sample-size guidance

Per scenario, plan for:
- baseline + treatment x at least 2 models = at least 4 trials per scenario
- 3 scenarios x 4 trials = 12 trials minimum

This sample is the bare minimum for a qualitative claim like "treatment
flipped GPT-5 from FAIL to PASS on 2 of 3 scenarios." It is NOT enough to
make a numeric claim like "treatment improves pass rate by N%."

For a study-grade claim, plan for at least 5 fresh chats per model per
condition (n=30 trials per scenario), and use the API harness when the
key returns.

## Honesty about limits

- ChatGPT and Gemini inject hidden system instructions you cannot see. If
  treatment fails to show a treatment effect, one possible explanation is
  that the hidden system instructions are already biasing the model in
  the same direction as form-check. You cannot disentangle this from web.
- Web models route to different backend variants depending on time of day,
  load, and account tier. Same model name, different actual model.
- Copy/paste from the browser sometimes loses formatting. If a model
  response uses code blocks heavily, save as plain text and verify
  pass_criteria.py is matching the right substrings.
