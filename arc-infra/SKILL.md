---
name: arc-infra
description: Spin up an ephemeral Shadeform GPU instance via arc-infra to run a larger experiment, then tear it down. Use whenever an experiment needs a GPU or more compute/memory than this box has — the pattern is always create box → run → collect results → delete box. Instances up to A100 SXM need no approval; anything larger requires asking Wilson first.
---

# Ephemeral Shadeform GPU boxes (arc-infra)

Run larger experiments on short-lived Shadeform instances managed with the
arc-infra CLI. The CLI is invoked as `python3 -m arc_infra.cli` (the README's
`c` alias only exists in interactive shells; commands below use `c` for
brevity). Full reference: `~/arc-infra/README.md`.

## Hard rules

1. **Naming.** Every instance name must be `wilson-auto-<suffix>` where
   `<suffix>` is a short informative slug, at most ~20 chars, lowercase with
   hyphens: `wilson-auto-llama-ft`, `wilson-auto-gsm8k-eval`. This marks boxes
   as Wilson's and auto-created so other people don't have to guess.
2. **Approval boundary.** GPU types up to and including A100 SXM (A100, A100_80G
   and their SXM variants, or anything smaller — A10, A6000, L40S, ...) may be
   created without asking. Anything beyond an A100 SXM — H100, H200, B200,
   GB200, or unusually large multi-node setups — requires asking Wilson and
   receiving explicit approval first. Ask in your reply and wait for the follow-up message;
   do not create the instance speculatively.
   ⚠️ The CLI's default `--gpu-type` glob is `'*100*'`, which matches H100 too.
   Always pass an explicit `--gpu-type`.
3. **At most 1×A100 per conversation.** Within one conversation/session you may
   have at most one A100 provisioned without approval: no multi-A100 boxes
   (`--num-gpus 1` only for A100s) and no second A100 box while yours is up.
   Needing more in the same conversation requires asking Wilson first. A100s
   already running from *other* conversations don't count against you — if
   `c list` shows other `wilson-auto-*` boxes, leave them alone and proceed
   (and never delete a box you didn't create).
4. **Artifacts live under the configured `RUN_ROOT_BLOB` prefix.** Read it
   from `~/.arc_infra_config.py`; do not invent a replacement prefix. Prefer
   `c run` with `--run-name`, which lands results there automatically.
   Anything you copy to blob storage manually (blobfile / boostedblob /
   `gcloud storage`) must also go under that prefix.
5. **No idling — boxes cost money the entire time they exist.** Create as late
   as possible, delete as soon as results are safely off the box. Delete on
   failure paths too: a crashed experiment still ends with `c delete`. Before
   finishing any task in which you created instances, run `c list` and delete
   every `wilson-auto-*` box you created. The only exception is Wilson
   explicitly asking for a box to be kept alive — in that case your final
   reply must name the box, why it's still up, and the exact delete command.

## Standard lifecycle

```bash
# 1. Create (add --auto to retry every minute until capacity is found)
python3 -m arc_infra.cli create wilson-auto-myexp --num-gpus 1 --gpu-type A100_80G --auto

# 2. (Optional) set up from ~/.arc_infra_config.py: blob auth + code rsync + startup script
python3 -m arc_infra.cli setup wilson-auto-myexp     # or `launch` = create + setup
python3 -m arc_infra.cli wait wilson-auto-myexp      # block until startup script finishes

# 3. Run the experiment
python3 -m arc_infra.cli run wilson-auto-myexp path/to/script.py --run-name myexp-001
python3 -m arc_infra.cli tail wilson-auto-myexp      # watch output
#    ...or ad-hoc commands:
python3 -m arc_infra.cli ssh wilson-auto-myexp 'nvidia-smi'

# 4. Collect results BEFORE deleting
#    `c run` with --run-name auto-syncs *.txt/.log/.csv/.json/.jsonl from
#    $RESULTS_DIR on the box to $RESULTS_BLOB_DIR under configured RUN_ROOT_BLOB.
#    For anything else, rsync it back:
python3 -m arc_infra.cli rsync wilson-auto-myexp:~/results ./results/

# 5. Delete, then verify nothing is left
python3 -m arc_infra.cli delete wilson-auto-myexp
python3 -m arc_infra.cli list
```

Other useful commands: `debug <name>` (provisioning issues), `kill <name>`
(stop all running functions), `blob-auth <name>` (12h GCS access),
`upload-code <name>` (rsync only, no startup script). On multi-GPU boxes
`c run` defaults to MPI with one rank per GPU; use `--num-gpus` to limit.

## Prerequisites / troubleshooting

- Auth is Google ADC: a `DefaultCredentialsError` means credentials are
  missing or expired — tell Wilson to run
  `gcloud auth login --no-launch-browser` and
  `gcloud auth application-default login --no-launch-browser`
  (gcloud lives at `/snap/bin/gcloud`). Don't attempt to work around it.
- `Permission denied on resource project None` means `gcloud` isn't on PATH:
  google-auth shells out to gcloud to discover the project. Ensure `/snap/bin`
  is on PATH.
- The package is installed editable from `~/arc-infra` (`import arc_infra`).
- Long runs: prefer `c run` + `--run-name` so results stream to blob storage
  as they're produced — if the box dies or the session times out, partial
  results survive. Check progress with `c tail`.
