# how to

first of all install a virtual machine running freebsd.
Adopt the settings in the bootstrap inventory and run

    ansible-playbook -i inventory/hosts env.yml --limit <vm-hostname>

As soon as the freebsd machine is up and running you're able to create your first
jail template

    ansible-playbook -i inventory/hosts tasks/jails/base/create/main.yml --limit <vm-hostname>

## optional

It's up to you if you want to manage your inventory in a static file driven structure or migrate
everything into a full encrypted key-value store.

    ansible-playbook -i inventory/hosts tasks/jails/create/main.yml
      --limit <vm-hostnam>
      --extra-vars="jail_stage=prod jail_name=vault"

the above command only creates a jail that can be started without applying the roles assigned to that jail.
After the jail is started you should be able to apply it's roles.

    ansible-playbook -i inventory/hosts prod.yml --limit <jail-hostname>

If your consul and vault role are applied you have to finish the first run wizard on http://<jail-hostname>:8200
and copy all contents of the bootstrap env into a newly created key-value secret engine
called `ansible`

### vault hierarchy

    ansible
     `host_vars
      `foo.example.org
     `group_vars
      `vault
     `inventory
      `consul
      `vault

an example host_vars file looks like this

    {
      "ipv4addr": "1.2.3.4"
    }

an example group_vars file looks similar while a inventory file requires
to contain either a `hosts` or a `children` element.

    {
      "hosts": [
        "foo.example.org"
      ],
      "children": [
        "consul"
      ]
    }

After copying your initial inventory over you can run ansible with a dynamic inventory stored in
hashicorp's vault

    export VAULT_ADDR="http://<vault-hostname>:8200"
    export VAULT_TOKEN="<token>"

    ansible-playbook -i vaultinventory.py env.yml
