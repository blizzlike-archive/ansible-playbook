#!/usr/bin/env python

import argparse
import json
import requests
import os

class VaultClient():
  def __init__(self, addr, token):
    self.addr = addr
    self.token = token

  def list(self, path):
    resp = requests.request(
      method = 'LIST',
      url = self.addr + '/v1/' + path,
      headers = { "X-Vault-Token": self.token })

    if resp.status_code == 200:
      return resp.json()['data']['keys']

    return {}

  def read(self, path):
    resp = requests.request(
      method = 'GET',
      url = self.addr + '/v1/' + path,
      headers = { "X-Vault-Token": self.token })

    if resp.status_code == 200:
      return resp.json()['data']

    return {}

class VaultInventory():
  def __init__(self):
    self.inventory = {
      'all': {
        'hosts': [], 'children': []
      },
      '_meta': {
        'hostvars': {}
      }
    }

    addr = os.environ['VAULT_ADDR']
    token = os.environ['VAULT_TOKEN']

    if not addr or not token:
      return False

    self.client = VaultClient(
      addr = addr, token = token)

  def createInventory(self):
    grouplist = self.client.list(path = 'ansible/inventory')
    for g in grouplist:
      self.inventory[g] = self.client.read(path = 'ansible/inventory/' + g)
      self.inventory[g]['vars'] = self.client.read(path = 'ansible/group_vars/' + g)

      self.inventory['all']['children'].append(g)
      if 'hosts' in self.inventory[g]:
        for h in self.inventory[g]['hosts']:
          if h not in self.inventory['all']['hosts']:
            self.inventory['all']['hosts'].append(h)

          self.inventory['_meta']['hostvars'][h] = self.client.read(
            path = 'ansible/host_vars/' + h)

    self.inventory['all']['vars'] = self.client.read(path = 'ansible/group_vars/all')

  def run(self):
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action= 'store_true')
    parser.add_argument('--host', action= 'store')
    args = parser.parse_args()

    if args.list:
      self.createInventory()

      print(json.dumps(self.inventory))

if __name__ == '__main__':
  VaultInventory().run()
