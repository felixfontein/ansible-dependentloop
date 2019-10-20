# ansible-dependentloop

This is a small [Ansible](https://github.com/ansible/ansible)
[lookup plugin](http://docs.ansible.com/ansible/playbooks_lookups.html) which
allows to do nested loops where the inner loops depend on the current `item` of
the outer loops.

(That's something which is unfortunately not supported by Ansible by default,
but sometimes needed, for example for more complex deployment setups.)

The current version requires Ansible 2.9 (and will stop printing deprecation
warnings for Ansible 2.9). Older versions work with Ansible >= 2.0.

See `ansible.cfg.sample` for how to include this plugin into your local Ansible
setup.

This plugin allows you to write something like:

    - name: Test
      debug: msg="{{ item.0 }} {{ item.1 }} {{ item.2 }}"
      with_dependent:
      - "[1, 2]"
      - "[item.0 + 3, item.0 + 6]"
      - "[item.0 + item.1 * 10]"

in a playbook. This yields the following output:

    ok: [localhost] => (item={0: 1, 1: 4, 2: 41}) => {
        "item": {
            "0": 1, 
            "1": 4, 
            "2": 41
        }, 
        "msg": "1 4 41"
    }
    ok: [localhost] => (item={0: 1, 1: 7, 2: 71}) => {
        "item": {
            "0": 1, 
            "1": 7, 
            "2": 71
        }, 
        "msg": "1 7 71"
    }
    ok: [localhost] => (item={0: 2, 1: 5, 2: 52}) => {
        "item": {
            "0": 2, 
            "1": 5, 
            "2": 52
        }, 
        "msg": "2 5 52"
    }
    ok: [localhost] => (item={0: 2, 1: 8, 2: 82}) => {
        "item": {
            "0": 2, 
            "1": 8, 
            "2": 82
        }, 
        "msg": "2 8 82"
    }
