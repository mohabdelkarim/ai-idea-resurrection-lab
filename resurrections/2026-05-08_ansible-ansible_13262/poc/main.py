"""
PoC: Loop over blocks in Ansible (ansible/ansible#13262)

This script simulates the correct implementation path for adding
loop support to blocks in Ansible's PlayIterator / TaskExecutor.

No Ansible installation required — pure Python simulation.
"""

# ---------------------------------------------------------------------------
# Minimal stubs mirroring Ansible internals
# ---------------------------------------------------------------------------

class Task:
    def __init__(self, name, loop_var=None):
        self.name = name
        self.loop_var = loop_var

    def __repr__(self):
        return f"Task({self.name!r})"


class Block:
    """Mirrors ansible.playbook.block.Block (simplified)."""
    def __init__(self, tasks, loop=None, loop_var="item"):
        self.tasks = tasks
        self.loop = loop        # e.g. ["web", "db", "cache"]
        self.loop_var = loop_var

    def get_tasks(self):
        return self.tasks


# ---------------------------------------------------------------------------
# Simulate the TaskExecutor loop-over-block logic
#
# Currently Ansible only supports `loop:` on individual tasks.
# The proposed change is to detect `loop:` on a Block and expand
# the block's tasks for each item, injecting `loop_var` into vars.
# This would live in:
#   lib/ansible/executor/task_executor.py  (_execute_regular())
#   lib/ansible/playbook/block.py          (compile())
# ---------------------------------------------------------------------------

def execute_block(block, variables=None):
    """Execute a block, optionally iterating if block.loop is set."""
    variables = variables or {}

    if block.loop:
        # NEW: iterate block over each item
        print(f"[block] Looping over {len(block.loop)} items (loop_var='{block.loop_var}')")
        for item in block.loop:
            print(f"  --- item: {item!r} ---")
            loop_vars = {**variables, block.loop_var: item}
            _run_tasks(block.get_tasks(), loop_vars)
    else:
        _run_tasks(block.get_tasks(), variables)


def _run_tasks(tasks, variables):
    for task in tasks:
        item_label = f" [item={variables.get('item')!r}]" if "item" in variables else ""
        print(f"    [run] {task.name}{item_label}")


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Simulation: loop over a block ===")
    print()

    # Before: you'd have to repeat tasks manually or use include_tasks hacks
    # After: loop: on the block expands all tasks inside
    service_block = Block(
        tasks=[
            Task("Ensure service is installed"),
            Task("Copy config file"),
            Task("Enable and start service"),
        ],
        loop=["nginx", "postgresql", "redis"],
        loop_var="item"
    )

    execute_block(service_block)

    print()
    print("=== Block without loop (existing behaviour unchanged) ===")
    print()
    simple_block = Block(tasks=[Task("Run migrations"), Task("Restart app")])
    execute_block(simple_block)
