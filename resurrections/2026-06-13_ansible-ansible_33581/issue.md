# Name of task containing block is not printed to stdout

**Repository:** [ansible/ansible](https://github.com/ansible/ansible)
**Issue:** [ansible/ansible#33581](https://github.com/ansible/ansible/issues/33581)
**Reactions:** 52 👍
**Created:** 2017-12-05T14:05:02Z
**Last Activity:** 2024-07-01T13:00:02Z
**Labels:** test, support:community, feature, bot_closed

---

## Original Description

##### ISSUE TYPE
 - Feature Idea



##### COMPONENT NAME
Ansible Blocks

##### ANSIBLE VERSION
```
ansible 2.4.0.0
  config file = /etc/ansible/ansible.cfg
  configured module search path = [~/.ansible/plugins/modules', u'/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python2.7/site-packages/ansible
  executable location = /usr/bin/ansible
  python version = 2.7.5 (default, May  3 2017, 07:55:04) [GCC 4.8.5 20150623 (Red Hat 4.8.5-14)]
```

##### CONFIGURATION
<!---
If using Ansible 2.4 or above, paste the results of "ansible-config dump --only-changed"

Otherwise, mention any settings you have changed/added/removed in ansible.cfg
(or using the ANSIBLE_* environment variables).

-->

##### OS / ENVIRONMENT
Red Hat Enterprise Linux Server release 7.4 (Maipo) (master and target)

##### SUMMARY
When a block is included in a named task the stdout when running the playbook does not include the name of the task containing the block.

##### STEPS TO REPRODUCE
```
- name: apply-custom-error-pages
  block:
    - copy:
        src=files/{{ env }}/404.jsp
        dest={{ liferay_webapps_portal }}
      notify:
        - apply-puppet-config
    - copy:
        src=files/{{ env }}/500.html
        dest={{ liferay_webapps_portal }}
      notify:
        - apply-puppet-config
```

##### EXPECTED RESULTS
The task name is echoed to stdout, perhaps with output like follows:
```
TASK [base-liferay : apply-custom-error-pages : copy] *******************************************************************************************************************************************************************************
changed: [hostname]

TASK [base-liferay : apply-custom-error-pages : copy] *******************************************************************************************************************************************************************************
changed: [hostname]
```
##### ACTUAL RESULTS
The task name is not echoed to stdout

```
TASK [base-liferay : copy] *******************************************************************************************************************************************************************************
changed: [hostname]

TASK [base-liferay : copy] *******************************************************************************************************************************************************************************
changed: [hostname]
```


---

*Resurrected by Resurrection Bot 🧬*
