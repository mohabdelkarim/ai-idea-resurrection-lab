# feature request: looping over blocks

**Repository:** [ansible/ansible](https://github.com/ansible/ansible)
**Issue:** [ansible/ansible#13262](https://github.com/ansible/ansible/issues/13262)
**Reactions:** 350 👍
**Created:** 2015-11-23T17:43:27Z
**Last Activity:** 2020-12-03T21:47:08Z
**Labels:** affects_2.0, c:playbook/block, c:playbook/loop_control, support:core, feature

---

## Original Description

##### Issue Type:

Feature Idea

##### Component Name:
blocks

##### Ansible Version:

Ansible 2.0.0_rc-1
##### Ansible Configuration:

NA
##### Environment:

Ubuntu 15.10

##### Summary of Decision:

We're open to implementing this but want it to go through the proposal process.  Please see: https://github.com/ansible/ansible/issues/13262#issuecomment-335904803 for details.

##### Summary:

There are a number of use-cases where it would be valuable to be able to loop over a block of tasks, such that a few tasks are done in order, and that specific block of tasks are looped over for some set of values. It seems that the new block functionality could lend itself well to this if you were to enable looping over blocks.
##### Steps To Reproduce:

``` yaml
- hosts: localhost
  connection: local
  tasks:
  - block:
    - debug: msg="task 1 loop {{item}}"
    - debug: msg="task 2 loop {{item}}"
    with_items:
    - "1"
    - "2"
```
##### Expected Results:

```
PLAY ***************************************************************************

TASK [setup] *******************************************************************
ok: [localhost]

TASK [debug msg=task 1 loop {{item}}] ******************************************
ok: [localhost] => {
    "changed": false, 
    "msg": "task 1 loop 1"
}

TASK [debug msg=task 2 loop {{item}}] ******************************************
ok: [localhost] => {
    "changed": false, 
    "msg": "task 2 loop 1"
}

TASK [debug msg=task 1 loop {{item}}] ******************************************
ok: [localhost] => {
    "changed": false, 
    "msg": "task 1 loop 2"
}

TASK [debug msg=task 2 loop {{item}}] ******************************************
ok: [localhost] => {
    "changed": false, 
    "msg": "task 2 loop 2"
}

PLAY RECAP *********************************************************************
localhost                  : ok=5    changed=0    unreachable=0    failed=0
```
##### Actual Results:

```
ERROR! 'with_items' is not a valid attribute for a Block

The error appears to have been in '/root/test.yml': line 5, column 5, but may
be elsewhere in the file depending on the exact syntax problem.

The offending line appears to be:

  tasks:
  - block:
    ^ here
```


---

*Resurrected by Resurrection Bot 🧬*
