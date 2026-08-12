### Trainer notes
- **Program notes**: <one‑sentence description of the change>.
- **Your form**: 
- **Next session**: 

verdict=APPROVE

head=<7‑char‑sha>            # e.g. head=f227921

trainer-codereview-<org>-<branch‑slug>   # auto‑generated marker, e.g. trainer-codereview-weijia-89-trainer-skill-feat-post-push-merged-pr-guard

### Bug inventory
No P0–P4 findings: <short reason, e.g. "guard script blocks push when merged PR detected.">

### Automated verification
- [x] `GITHUB_ACTIONS=true GITHUB_WORKSPACE=$PWD bash scripts/verify_trainer_sync.sh`

### R‑6 waived
<!-- optional – include only if docs are not updated; otherwise delete this line -->
R-6 waived