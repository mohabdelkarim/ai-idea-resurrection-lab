# Support running ansible-test on collections outside a collection root

**Repository:** [ansible/ansible](https://github.com/ansible/ansible)
**Issue:** [ansible/ansible#60215](https://github.com/ansible/ansible/issues/60215)
**Reactions:** 54 👍
**Created:** 2019-08-07T15:35:37Z
**Last Activity:** 2024-07-01T13:00:02Z
**Labels:** support:core, has_pr, feature, bot_closed, affects_2.14

---

## Original Description

##### SUMMARY

When I develop my Ansible Collections, I want to be able to use a typical development workflow:

  1. `git clone [my project] [local folder]`
  2. `cd [local folder]`
  3. `ansible-test integration` (or whatever other command for local testing)

Currently, if I do this I get the following error:

```
 10:23:35 ~/Dropbox/VMs/collections/geerlingguy.php_roles $ ansible-test
ERROR: The current working directory must be at or below one of:

 - Ansible source: /Users/jgeerling/Downloads/ansible/
 - Ansible collection: {...}/ansible_collections/{namespace}/{collection}/

Current working directory: /Users/jgeerling/Dropbox/VMs/collections/geerlingguy.php_roles
```

I feel like this presents a pretty significant burden on collection maintainers and contributors, because a _very_ common workflow (especially if I'm not on my main workstation for some reason) is: clone repo, hack on it, run integration tests, commit changes, push to PR.

If I have to create an arbitrary directory structure, then clone into that structure, it's a lot of overhead. Other existing testing tools like `molecule` (or in other languages, Mocha for Node, PHPUnit or Behat for PHP, etc.) are self-contained and run from within the project directory without issue...

##### ISSUE TYPE
Feature Idea

##### COMPONENT NAME
ansible-test

##### ANSIBLE VERSION
<!--- Paste verbatim output from "ansible --version" between quotes -->
```paste below
$ ansible --version
ansible 2.9.0.dev0
  config file = /etc/ansible/ansible.cfg
  configured module search path = [u'/Users/jgeerling/.ansible/plugins/modules', u'/usr/share/ansible/plugins/modules']
  ansible python module location = /Users/jgeerling/Downloads/ansible/lib/ansible
  executable location = /Users/jgeerling/Downloads/ansible/bin/ansible
  python version = 2.7.16 (default, Apr 12 2019, 15:32:40) [GCC 4.2.1 Compatible Apple LLVM 10.0.1 (clang-1001.0.46.3)]
```

##### CONFIGURATION
<!--- Paste verbatim output from "ansible-config dump --only-changed" between quotes -->
```paste below
ANSIBLE_NOCOWS(/etc/ansible/ansible.cfg) = True
ANSIBLE_PIPELINING(/etc/ansible/ansible.cfg) = True
ANSIBLE_SSH_CONTROL_PATH(/etc/ansible/ansible.cfg) = /tmp/ansible-ssh-%%h-%%p-%%r
DEFAULT_FORKS(/etc/ansible/ansible.cfg) = 20
DEFAULT_HOST_LIST(/etc/ansible/ansible.cfg) = [u'/etc/ansible/hosts']
DEFAULT_ROLES_PATH(/etc/ansible/ansible.cfg) = [u'/Users/jgeerling/Dropbox/VMs/roles']
RETRY_FILES_ENABLED(/etc/ansible/ansible.cfg) = False
```

##### OS / ENVIRONMENT
<!--- Provide all relevant information below, e.g. target OS versions, network device firmware, etc. -->
macOS 10.14.5


##### STEPS TO REPRODUCE

  1. `git clone https://github.com/geerlingguy/ansible-collection-php_roles.git ansible-collection-php_roles`
  2. `cd ansible-collection-php_roles`
  3. `ansible-test integration`

##### EXPECTED RESULTS

Integration tests, if any, would be run.

##### ACTUAL RESULTS

```
$

---

*Resurrected by Resurrection Bot 🧬*
