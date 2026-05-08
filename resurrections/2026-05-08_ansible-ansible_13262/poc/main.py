import json
import os
from ansible.module_utils.basic import AnsibleModule
from ansible.executor.task_executor import TaskExecutor
from ansible.playbook.block import Block
from ansible.playbook.play_context import MAGIC_VARIABLE_MAPPING
from ansible.plugins.loader import get_connection_loader

class LoopableBlock(Block):
    def __init__(self, *args, **kwargs):
        super(LoopableBlock, self).__init__(*args, **kwargs)
        self.loop = None
        self.loop_var = None

    def loop_over(self, loop, loop_var):
        self.loop = loop
        self.loop_var = loop_var

    def run(self, play_context, runner_context, variables):
        if self.loop:
            return self._run_loop(play_context, runner_context, variables)
        else:
            return super(LoopableBlock, self).run(play_context, runner_context, variables)

    def _run_loop(self, play_context, runner_context, variables):
        results = []
        for item in self.loop:
            variables[self.loop_var] = item
            task_results = super(LoopableBlock, self).run(play_context, runner_context, variables)
            results.append(task_results)
        return results

def main():
    argument_spec = dict(
        loop=dict(type='list'),
        loop_var=dict(type='str')
    )

    module = AnsibleModule(argument_spec=argument_spec)
    loop = module.params['loop']
    loop_var = module.params['loop_var']

    block = LoopableBlock()
    block.loop_over(loop, loop_var)

    play_context = play_context = MAGIC_VARIABLE_MAPPING['play_context']
    runner_context = None
    variables = {}

    try:
        results = block.run(play_context, runner_context, variables)
        module.exit_json(results=results)
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()