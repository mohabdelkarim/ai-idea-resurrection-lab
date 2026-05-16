"""
PoC: meta: end_role for Ansible

This script demonstrates the correct implementation path by:
1. Showing the new AnsibleEndRole exception class
2. Showing the patch to _execute_meta() in TaskExecutor
3. Running a minimal simulation of role task execution that honours end_role

This is NOT a runnable Ansible module. It is a standalone simulation
that exercises the control-flow logic without requiring a full Ansible install.
"""

# ---------------------------------------------------------------------------
# 1. Exception (mirrors AnsibleEndHost in ansible/errors/__init__.py)
# ---------------------------------------------------------------------------
class AnsibleError(Exception):
    pass

class AnsibleEndPlay(AnsibleError):
    pass

class AnsibleEndHost(AnsibleError):
    pass

class AnsibleEndRole(AnsibleError):
    """New exception: stops the current role, play continues."""
    pass


# ---------------------------------------------------------------------------
# 2. Minimal task / role stubs
# ---------------------------------------------------------------------------
class Task:
    def __init__(self, name, meta_action=None, condition=True, role=None):
        self.name = name
        self.meta_action = meta_action  # e.g. 'end_role', 'end_play'
        self.condition = condition       # simulates 'when:'
        self.role = role

    @property
    def is_meta(self):
        return self.meta_action is not None


class Role:
    def __init__(self, name, tasks):
        self.name = name
        self.tasks = tasks


# ---------------------------------------------------------------------------
# 3. Simulate _execute_meta() — the patch site in task_executor.py
# ---------------------------------------------------------------------------
def _execute_meta(task):
    """Mirrors TaskExecutor._execute_meta() with end_role support added."""
    action = task.meta_action
    if action == 'end_play':
        raise AnsibleEndPlay()
    elif action == 'end_host':
        raise AnsibleEndHost()
    elif action == 'end_role':
        if task.role is None:
            raise AnsibleError("meta: end_role can only be used inside a role")
        raise AnsibleEndRole()
    else:
        raise AnsibleError(f"Unknown meta action: {action}")


# ---------------------------------------------------------------------------
# 4. Simulate strategy/linear.py role task runner
# ---------------------------------------------------------------------------
def execute_role(role):
    """Simulate executing a role's tasks, honouring end_role."""
    print(f"[role:{role.name}] Starting")
    for task in role.tasks:
        if not task.condition:
            print(f"  [skip] {task.name} (condition false)")
            continue
        try:
            if task.is_meta:
                _execute_meta(task)
            else:
                print(f"  [run]  {task.name}")
        except AnsibleEndRole:
            print(f"  [end_role] Stopping role '{role.name}' early")
            return  # <-- key: exits role, play continues
        except AnsibleEndPlay:
            print(f"  [end_play] Stopping entire play")
            raise   # re-raise to stop the play
    print(f"[role:{role.name}] Completed normally")


def execute_play(roles):
    """Simulate a play executing a list of roles."""
    try:
        for role in roles:
            execute_role(role)
    except AnsibleEndPlay:
        print("[play] Stopped by end_play")
    print("[play] Done")


# ---------------------------------------------------------------------------
# 5. Demo
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    preflight_role = Role(
        name="preflight",
        tasks=[
            Task("Check if already configured"),
            # Simulates: meta: end_role  when: already_configured.stat.exists
            Task("Exit early — already configured",
                 meta_action="end_role",
                 condition=True,   # <-- set to False to see full role run
                 role="preflight"),
            Task("Run expensive setup (should be SKIPPED)"),
        ]
    )

    deploy_role = Role(
        name="deploy",
        tasks=[
            Task("Deploy application"),
            Task("Restart service"),
        ]
    )

    print("=== Simulation: end_role stops only the current role ===")
    print()
    execute_play([preflight_role, deploy_role])
