import json
import os
import sys
from ansible import constants as C
from ansible.plugins.action import ActionBase
from ansible.plugins.strategy import StrategyBase
from ansible.utils.sentinel import Sentinel
from ansible.utils.unsafe_proxy import AnsibleUnsafeBytesIO, AnsibleUnsafeText
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play_context import PlayContext
from ansible.playbook.play import Play
from ansible.executor.task_executor import TaskExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.utils.vars import VariableManager

class BlockTaskExecutor(TaskExecutor):
    def __init__(self, *args, **kwargs):
        super(BlockTaskExecutor, self).__init__(*args, **kwargs)

    def _run_task(self, play_context, task_vars=None):
        if task_vars is None:
            task_vars = {}
        result = super(BlockTaskExecutor, self)._run_task(play_context, task_vars)
        if self._task._parent:
            task_name = self._task._parent.get_name()
            result['task_name'] = task_name
        return result

class BlockStrategy(StrategyBase):
    def __init__(self, *args, **kwargs):
        super(BlockStrategy, self).__init__(*args, **kwargs)

    def _execute_task(self, task, play_context, task_vars=None, callback=None):
        if task_vars is None:
            task_vars = {}
        executor = BlockTaskExecutor(task, play_context, self._connection, self._task_vars_cache, self._playbook_dir, self._loader)
        result = executor.run()
        return result

def main():
    try:
        inventory = InventoryManager(loader=DataLoader(), sources='inventory.ini')
        play_context = PlayContext()
        play = Play().load('playbook.yml', variable_manager=VariableManager(), loader=DataLoader())
        tqm = TaskQueueManager(inventory=inventory, play=play, play_context=play_context, loader=DataLoader())
        strategy = BlockStrategy(tqm, inventory, play, play_context, DataLoader())
        task = Play().load_tasks('task.yml', variable_manager=VariableManager(), loader=DataLoader())[0]
        result = strategy._execute_task(task, play_context)
        print(json.dumps(result, indent=4))
    except Exception as e:
        print('Error: %s' % str(e))
if __name__ == '__main__':
    main()