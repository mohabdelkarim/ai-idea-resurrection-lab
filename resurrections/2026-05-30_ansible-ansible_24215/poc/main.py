import json
import logging
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play_context import MAGIC_VARIABLE_MAPPING
from ansible.plugins.action import ActionBase
from ansible.plugins.strategy import StrategyBase
from ansible.utils.sentinel import Sentinel

class VerbosityAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super(VerbosityAction, self).__init__(*args, **kwargs)
        self._verbosity = self._task_vars.get('verbosity')

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = {}
        self._task_vars = task_vars
        verbosity = self._verbosity
        if verbosity is not None:
            logging.basicConfig(level=logging.DEBUG + verbosity * 10)
        else:
            logging.basicConfig(level=logging.INFO)
        return dict(ansible_verbosity=self._verbosity)

class VerbosityStrategy(StrategyBase):
    def __init__(self, *args, **kwargs):
        super(VerbosityStrategy, self).__init__(*args, **kwargs)

    def _execute_task(self, task, play_context):
        verbosity = task.vars.get('verbosity')
        if verbosity is not None:
            play_context.verbosity = verbosity
        return super(VerbosityStrategy, self)._execute_task(task, play_context)

def main():
    try:
        loader = DataLoader()
        playbook = '---
- name: Test verbosity
  hosts: localhost
  tasks:
  - name: Task 1
    debug:
      msg: Task 1
    verbosity: 1
  - name: Task 2
    debug:
      msg: Task 2
'
        with open('playbook.yml', 'w') as f:
            f.write(playbook)
        command = 'ansible-playbook -i localhost, playbook.yml'
        print(command)
    except Exception as e:
        print('Error: %s' % e)

if __name__ == '__main__':
    main()