import logging
import json
from ansible.executor.task_executor import TaskExecutor
from ansible.playbook.play_context import MAGIC_VARIABLE_MAPPING
from ansible.plugins.strategy import StrategyBase
from ansible.utils.sentinel import Sentinel

class BlockTaskExecutor(TaskExecutor):
    def __init__(self, *args, **kwargs):
        super(BlockTaskExecutor, self).__init__(*args, **kwargs)
        self._task_vars = kwargs.get('task_vars', {})

    def _run_task(self):
        result = super(BlockTaskExecutor, self)._run_task()
        if self._task:
            task_name = self._task.get_name()
            if task_name:
                logging.info('TASK [%s : %s] *******************************************************************************************************************************************************************************',
                             self._task._play.get_name(), task_name)
        return result

class BlockStrategy(StrategyBase):
    def __init__(self, *args, **kwargs):
        super(BlockStrategy, self).__init__(*args, **kwargs)

    def _execute_task(self, task, host):
        executor = BlockTaskExecutor(task, host, self._connection, self._task_vars)
        return executor.run()

def main():
    try:
        # Example usage
        task = Sentinel()
        task.set_name('example_task')
        play = Sentinel()
        play.get_name = lambda: 'example_play'
        task._play = play
        task_vars = {}
        executor = BlockTaskExecutor(task, 'localhost', None, task_vars)
        executor._run_task()
    except Exception as e:
        logging.error('Error: %s', str(e))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()