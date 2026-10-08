# Audit logs

## Summary

[`audit-run.json`](audit-run.json) records the outputs and measurements retained
from the first audit on 2026-10-08. The original terminal stream was not saved
as one raw file. The record distinguishes observed outputs from explanatory
notes and does not reconstruct missing terminal text.

Run `../scripts/reproduce.sh` to produce a fresh full log. That script writes
each command and its output under the chosen working directory.
