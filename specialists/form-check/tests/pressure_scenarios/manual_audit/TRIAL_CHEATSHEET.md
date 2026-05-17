# Trial cheatsheet (12 trials, ~60 minutes)

Models: ChatGPT (GPT-5 web), Gemini 2.5 Pro web.
Scenarios: 3 (the v0.3.1 set).
Conditions: 2 (baseline, treatment).
Total: 2 x 3 x 2 = 12 trials. Plan ~5 min per trial.

## Fresh-chat URLs (use a NEW chat for EVERY trial)

- ChatGPT (temporary chat): https://chatgpt.com/?temporary-chat=true
- Gemini: https://gemini.google.com/app (click the "New chat" button after each trial)

Why fresh chat per trial: reusing a chat between baseline and treatment pollutes the treatment with baseline context. The whole point of the baseline/treatment split is to isolate the form-check effect.

## Per-trial loop (5 minutes)

For each row in the table below:

1. Run the prep command. This puts the prompt on your clipboard.
   ```
   bash prep_trial.sh <SHORTNAME> <CONDITION>
   ```
2. Open the model's URL in a fresh chat.
3. Paste (Cmd+V) and send.
4. Wait for the full response.
5. Select all of the response text and copy.
6. Save to the suggested response file (paths below).
7. Score with the wrapper:
   ```
   bash manual_audit.sh <SHORTNAME> <MODEL> <CONDITION> <RESPONSE_FILE>
   ```

## 12-trial run order (recommended)

The order interleaves models so any time-of-day routing variance hits both equally. Within each model, baseline-then-treatment is run scenario-by-scenario.

| # | Model | Scenario | Condition | Prep command | Response file | Score command |
|---|---|---|---|---|---|---|
| 1 | gpt-5 | 01 | baseline | `bash prep_trial.sh 01_red-flag_upstream-constraint-missed baseline` | `runs/gpt-5/01/baseline.txt` | `bash manual_audit.sh 01_red-flag_upstream-constraint-missed gpt-5 baseline runs/gpt-5/01/baseline.txt` |
| 2 | gemini-2.5-pro | 01 | baseline | `bash prep_trial.sh 01_red-flag_upstream-constraint-missed baseline` | `runs/gemini-2.5-pro/01/baseline.txt` | `bash manual_audit.sh 01_red-flag_upstream-constraint-missed gemini-2.5-pro baseline runs/gemini-2.5-pro/01/baseline.txt` |
| 3 | gpt-5 | 01 | treatment | `bash prep_trial.sh 01_red-flag_upstream-constraint-missed treatment` | `runs/gpt-5/01/treatment.txt` | `bash manual_audit.sh 01_red-flag_upstream-constraint-missed gpt-5 treatment runs/gpt-5/01/treatment.txt` |
| 4 | gemini-2.5-pro | 01 | treatment | `bash prep_trial.sh 01_red-flag_upstream-constraint-missed treatment` | `runs/gemini-2.5-pro/01/treatment.txt` | `bash manual_audit.sh 01_red-flag_upstream-constraint-missed gemini-2.5-pro treatment runs/gemini-2.5-pro/01/treatment.txt` |
| 5 | gpt-5 | 02 | baseline | `bash prep_trial.sh 02_test-as-spec_test-locks-in-bug baseline` | `runs/gpt-5/02/baseline.txt` | `bash manual_audit.sh 02_test-as-spec_test-locks-in-bug gpt-5 baseline runs/gpt-5/02/baseline.txt` |
| 6 | gemini-2.5-pro | 02 | baseline | `bash prep_trial.sh 02_test-as-spec_test-locks-in-bug baseline` | `runs/gemini-2.5-pro/02/baseline.txt` | `bash manual_audit.sh 02_test-as-spec_test-locks-in-bug gemini-2.5-pro baseline runs/gemini-2.5-pro/02/baseline.txt` |
| 7 | gpt-5 | 02 | treatment | `bash prep_trial.sh 02_test-as-spec_test-locks-in-bug treatment` | `runs/gpt-5/02/treatment.txt` | `bash manual_audit.sh 02_test-as-spec_test-locks-in-bug gpt-5 treatment runs/gpt-5/02/treatment.txt` |
| 8 | gemini-2.5-pro | 02 | treatment | `bash prep_trial.sh 02_test-as-spec_test-locks-in-bug treatment` | `runs/gemini-2.5-pro/02/treatment.txt` | `bash manual_audit.sh 02_test-as-spec_test-locks-in-bug gemini-2.5-pro treatment runs/gemini-2.5-pro/02/treatment.txt` |
| 9 | gpt-5 | 03 | baseline | `bash prep_trial.sh 03_hallucination_library-behavior-unverified baseline` | `runs/gpt-5/03/baseline.txt` | `bash manual_audit.sh 03_hallucination_library-behavior-unverified gpt-5 baseline runs/gpt-5/03/baseline.txt` |
| 10 | gemini-2.5-pro | 03 | baseline | `bash prep_trial.sh 03_hallucination_library-behavior-unverified baseline` | `runs/gemini-2.5-pro/03/baseline.txt` | `bash manual_audit.sh 03_hallucination_library-behavior-unverified gemini-2.5-pro baseline runs/gemini-2.5-pro/03/baseline.txt` |
| 11 | gpt-5 | 03 | treatment | `bash prep_trial.sh 03_hallucination_library-behavior-unverified treatment` | `runs/gpt-5/03/treatment.txt` | `bash manual_audit.sh 03_hallucination_library-behavior-unverified gpt-5 treatment runs/gpt-5/03/treatment.txt` |
| 12 | gemini-2.5-pro | 03 | treatment | `bash prep_trial.sh 03_hallucination_library-behavior-unverified treatment` | `runs/gemini-2.5-pro/03/treatment.txt` | `bash manual_audit.sh 03_hallucination_library-behavior-unverified gemini-2.5-pro treatment runs/gemini-2.5-pro/03/treatment.txt` |

## Per-model account hygiene

ChatGPT:
- Use temporary chat URL above; it disables memory and history for that session.
- Verify the model selector reads GPT-5 (not 4o or a routed variant). If you only have GPT-4 / GPT-4o access, log the actual label in the model arg; do not call it gpt-5.
- Do NOT toggle browsing/canvas/data-analysis tools; we want plain chat behavior.

Gemini:
- Use a separate browser profile or incognito to avoid your stored Gem persona / Workspace context leaking in.
- Verify the model is "2.5 Pro" in the picker. If only Flash is available, log it as gemini-2.5-flash; results will differ.
- Disable any active "Gem" before pasting.

## When you are done

Aggregate the JSONL:

```bash
python3 -c '
import json, collections, pathlib
results = pathlib.Path("runs/results.jsonl").read_text().splitlines()
by_model_condition = collections.Counter()
totals = collections.Counter()
for line in results:
    if not line.strip(): continue
    r = json.loads(line)
    key = (r["model"], r["condition"])
    totals[key] += 1
    if r["verdict"] == "PASS": by_model_condition[key] += 1
for key in sorted(totals):
    print(f"{key[0]:20s} {key[1]:10s} {by_model_condition[key]}/{totals[key]}")
'
```

This gives you a 4-row table: each model x condition, pass-rate. Read it qualitatively only (n=3 per cell). Look for:

- Does treatment flip baseline FAIL to PASS for any scenario? That is the form-check effect.
- Does any scenario PASS in both conditions across both models? It does not discriminate; consider tightening pass_criteria.py.
- Does any scenario FAIL in both conditions across both models? Either form-check guidance is not strong enough to overcome the model's prior, or the pass_criteria.py is too strict; inspect the responses.

## What to do with the results

Whatever you find, the results live in `runs/results.jsonl` for this kit's lifetime. Optional: copy notable response transcripts to `runs/<model>/<scenario>/notes.md` with your qualitative read.
