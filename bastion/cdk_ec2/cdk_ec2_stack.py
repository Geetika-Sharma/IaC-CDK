import json
from pathlib import Path

from aws_cdk import (
    
    core,
    aws_ec2 as ec2, 

)
from constructs import Construct

# read config.json
path = Path(__file__).parent / "../config.json"
with path.open() as config_file:
    data = json.load(config_file)

instance_name=data['instance_name']
vpc_id=data['vpc_id']
instance_type=data['instance_type']
image_id=data['image_id']
availability_zone=data['availability_zone']
key_name=data['key_name']
subnet_id=data['subnet_id']


# read user_data.txt
path = Path(__file__).parent / "../user_data.txt"
with path.open() as user_data_file:
    user_data = user_data_file.read()

class Ec2InstanceStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # EC2 instance Shell Command
        instance_shellCommands = ec2.UserData.for_linux()
        instance_shellCommands.add_commands(user_data)

        # Lookup existing VPC
        vpc = ec2.Vpc.from_lookup(self,"vpc",vpc_id=vpc_id,)

        # Security group for instance
        instance_sg = ec2.CfnSecurityGroup(
            self,
            id="instance_sg",
            vpc_id=vpc_id,
            group_description="instance_sg",
            security_group_ingress=[
                ec2.CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp",
                    cidr_ip="0.0.0.0/0",
                    from_port=22,
                    to_port=22
                ),
                ec2.CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp",
                    cidr_ip="0.0.0.0/0",
                    from_port=80,
                    to_port=80
                ),
                ec2.CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp",
                    cidr_ip="0.0.0.0/0",
                    from_port=443,
                    to_port=443
                )
            ],
            tags=[{
                    "key": "Name",
                    "value": instance_name+'-sg'
            }]
        )

        # Create EC2 instance
        instance = ec2.CfnInstance(
            self,
            "ec2-instance",
            instance_type=instance_type,
            image_id=image_id,
            availability_zone=availability_zone,
            key_name=key_name,
            network_interfaces = [{
                "deviceIndex": "0",
                "associatePublicIpAddress": True,
                "subnetId": subnet_id,
                "groupSet": [instance_sg.ref]
            }],
            user_data=core.Fn.base64(instance_shellCommands.render()),
            tags=[{
                    "key": "Name",
                    "value": instance_name
            }]

        )

        # # Create EIP (instance)
        # instance_eip = ec2.CfnEIP(self, "instance-instance-eip")

        # # EIP Association (instance)
        # instance_1_eip_asso = ec2.CfnEIPAssociation(
        #     self,
        #     "instance-instance-eip-asso",
        #     eip=instance_eip.ref,
        #     instance_id=instance.ref,
        # )