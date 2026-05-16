# PoC: `meta: end_role`

This PoC simulates the correct implementation of `meta: end_role` in Ansible.

## What it demonstrates

- The `AnsibleEndRole` exception class that mirrors `AnsibleEndHost` / `AnsibleEndPlay`
- Where to patch `TaskExecutor._execute_meta()` (one `elif` branch)
- The control-flow: `end_role` stops the current role, the play continues with the next role

## How to run

No Ansible installation required — pure Python stdlib:

```bash
python poc/main.py
```

## Expected output

```
=== Simulation: end_role stops only the current role ===

[role:preflight] Starting
  [run]  Check if already configured
  [end_role] Stopping role 'preflight' early
[role:deploy] Starting
  [run]  Deploy application
  [run]  Restart service
[role:deploy] Completed normally
[play] Done
```

Change `condition=True` to `condition=False` on the `end_role` task to see the full preflight role run without early exit.
