import json
import os
from ansible.module_utils.basic import AnsibleModule, to_native
from ansible.errors import AnsibleError
from ansible.plugins.meta import MetaModule

class AnsibleMetaEndRole(MetaModule):
    def __init__(self, *args, **kwargs):
        super(AnsibleMetaEndRole, self).__init__(*args, **kwargs)
        self._singleton = True

    def run(self):
        self._end_role()
        return dict(changed=False)

    def _end_role(self):
        # Get the current play and role
        play = self._play
        role = self._role

        if role:
            # Notify the play to end the role
            play.end_role(role)
        else:
            raise AnsibleError('No role is currently being executed')

def main():
    argument_spec = dict()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    try:
        meta_end_role = AnsibleMetaEndRole(module)
        result = meta_end_role.run()
        module.exit_json(**result)
    except AnsibleError as e:
        module.fail_json(msg=to_native(e), **dict(failed=True))
    except Exception as e:
        module.fail_json(msg=to_native(e), **dict(failed=True))

if __name__ == '__main__':
    main()