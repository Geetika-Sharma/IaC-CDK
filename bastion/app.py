#!/usr/bin/env python3

import json
from pathlib import Path
from aws_cdk import core
from cdk_ec2.cdk_ec2_stack import Ec2InstanceStack

# read config.json
path = Path(__file__).parent / "config.json"
with path.open() as config_file:
    data = json.load(config_file)

account=data['account']
region=data['region']

app = core.App()
Ec2InstanceStack(app, "Ec2InstanceStack",
    env=core.Environment(account=account, region=region),
    )

app.synth()
