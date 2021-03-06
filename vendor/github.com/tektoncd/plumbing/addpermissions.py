#!/usr/bin/env python3

"""
addpermissions.py gives users access to the Tekton GCP projects

In order to interact with GCP resources
(https://github.com/tektoncd/plumbing/blob/master/README.md#gcp-projects)
folks sometimes need to be able to do actions like push images and view
a project in the web console.

This script will add the permissions allowed to folks on the governing board
(https://github.com/tektoncd/community/blob/master/governance.md#permissions-and-access)
to all GCP projects.


This script requires the `gcloud` command line tool and the python
`PyYaml` library.

Example usage:
  python3 addpermissions.py --users "andrea.frittoli@gmail.com, andrew.bayer@gmail.com, dlorenc@google.com, klewandowski@google.com, vdemeest@redhat.com, dibyajyoti@google.com, sbws@google.com"
"""
import argparse
import shlex
import shutil
import subprocess
import sys
import urllib.request
import yaml
from typing import List


ROLES = (
  "roles/container.admin",
  "roles/iam.serviceAccountUser",
  "roles/storage.admin",
  "roles/compute.storageAdmin",
  "roles/viewer",
)
KNOWN_PROJECTS = (
  "tekton-releases",
  "tekton-nightly",
)
BOSKOS_CONFIG_URL = "https://raw.githubusercontent.com/tektoncd/plumbing/master/boskos/boskos-config.yaml"


def gcloud_required() -> None:
  if shutil.which("gcloud") is None:
    sys.stderr.write("gcloud binary is required; https://cloud.google.com/sdk/install")
    sys.exit(1)


def add_to_all_projects(users: List[str], projects: List[str]) -> None:
  for user in users:
    for project in projects:
      for role in ROLES:
        subprocess.check_call(shlex.split(
            "gcloud projects add-iam-policy-binding {} --member user:{} --role {}".format(project, user, role)
        ))


def parse_boskos_projects() -> List[str]:
  config = urllib.request.urlopen(BOSKOS_CONFIG_URL).read()
  c = yaml.load(config)
  nested_config = c["data"]["config"]
  cc = yaml.load(nested_config)
  return cc["resources"][0]["names"]


if __name__ == '__main__':
  arg_parser = argparse.ArgumentParser(
      description="Give a user access to all plumbing resources")
  arg_parser.add_argument("--users", type=str, required=True,
                          help="The names of the users' accounts, usually their email address, comma separated")
  args = arg_parser.parse_args()

  gcloud_required()

  boskos_projects = parse_boskos_projects()

  add_to_all_projects([u.strip() for u in args.users.split(",")], list(KNOWN_PROJECTS) + boskos_projects)

