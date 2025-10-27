from __future__ import annotations

from typing import Optional, List
import base64

import pulumi
from pulumi import Output
import pulumi_aws as aws

# --------------------------------------------------------------------------------------
# 1) Descubrir VPC y subnets por defecto
# --------------------------------------------------------------------------------------
default_vpc: aws.ec2.GetVpcResult = aws.ec2.get_vpc(default=True)

default_subnets: aws.ec2.GetSubnetsResult = aws.ec2.get_subnets(
    filters=[aws.ec2.GetSubnetsFilterArgs(name="vpc-id", values=[default_vpc.id])]
)

# --------------------------------------------------------------------------------------
# 2) AMI de Amazon Linux 2 (x86_64) más reciente
# --------------------------------------------------------------------------------------
ami: aws.ec2.GetAmiResult = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[
        aws.ec2.GetAmiFilterArgs(name="name", values=["amzn2-ami-hvm-*-x86_64-gp2"]),
        aws.ec2.GetAmiFilterArgs(name="state", values=["available"]),
    ],
)

# --------------------------------------------------------------------------------------
# 3) Security Groups
# --------------------------------------------------------------------------------------
asg_sg: aws.ec2.SecurityGroup = aws.ec2.SecurityGroup(
    "asg-sg",
    description="Allow HTTP from anywhere",
    vpc_id=default_vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
            ipv6_cidr_blocks=["::/0"],
            description="HTTP",
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
            ipv6_cidr_blocks=["::/0"],
            description="all egress",
        )
    ],
)

alb_sg: aws.ec2.SecurityGroup = aws.ec2.SecurityGroup(
    "alb-sg",
    description="Allow HTTP to ALB",
    vpc_id=default_vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
            ipv6_cidr_blocks=["::/0"],
            description="HTTP to ALB",
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
            ipv6_cidr_blocks=["::/0"],
            description="all egress",
        )
    ],
)

# --------------------------------------------------------------------------------------
# 4) User data -> Base64
# --------------------------------------------------------------------------------------
user_data: str = """#!/bin/bash
set -xe
yum update -y
amazon-linux-extras install nginx1 -y || yum install -y nginx
echo "<h1>Hola desde $(hostname)</h1>" > /usr/share/nginx/html/index.html
systemctl enable nginx
systemctl start nginx
"""
user_data_b64: str = base64.b64encode(user_data.encode("utf-8")).decode("utf-8")

# --------------------------------------------------------------------------------------
# 5) Launch Template
# --------------------------------------------------------------------------------------
lt: aws.ec2.LaunchTemplate = aws.ec2.LaunchTemplate(
    "app-lt",
    name_prefix="app-lt-",
    image_id=ami.id,
    instance_type="t3.micro",
    vpc_security_group_ids=[asg_sg.id],
    user_data=pulumi.Output.secret(user_data_b64),
    update_default_version=True,
)

# --------------------------------------------------------------------------------------
# 6) ALB + Target Group + Listener
# --------------------------------------------------------------------------------------
tg: aws.lb.TargetGroup = aws.lb.TargetGroup(
    "app-tg",
    port=80,
    protocol="HTTP",
    target_type="instance",
    vpc_id=default_vpc.id,
    health_check=aws.lb.TargetGroupHealthCheckArgs(
        path="/",
        protocol="HTTP",
        matcher="200-399",
        interval=30,
        timeout=5,
        healthy_threshold=2,
        unhealthy_threshold=2,
    ),
)

alb: aws.lb.LoadBalancer = aws.lb.LoadBalancer(
    "app-alb",
    load_balancer_type="application",
    security_groups=[alb_sg.id],
    subnets=default_subnets.ids,
)

listener: aws.lb.Listener = aws.lb.Listener(
    "app-listener",
    load_balancer_arn=alb.arn,
    port=80,
    protocol="HTTP",
    default_actions=[
        aws.lb.ListenerDefaultActionArgs(type="forward", target_group_arn=tg.arn)
    ],
)

# --------------------------------------------------------------------------------------
# 7) Auto Scaling Group
# --------------------------------------------------------------------------------------
asg: aws.autoscaling.Group = aws.autoscaling.Group(
    "app-asg",
    desired_capacity=2,
    min_size=2,
    max_size=5,
    vpc_zone_identifiers=default_subnets.ids,
    health_check_type="ELB",
    target_group_arns=[tg.arn],
    launch_template=aws.autoscaling.GroupLaunchTemplateArgs(
        id=lt.id,
        version="$Latest",
    ),
    metrics_granularity="1Minute",
    termination_policies=["OldestInstance"],
)

# Asegurar orden lógico
_ensure_listener_before_asg: Output[Optional[None]] = Output.all(listener.arn).apply(lambda _: None)

# --------------------------------------------------------------------------------------
# 8) Políticas de Scaling
# 8a) Target Tracking por CPU (50%)
# --------------------------------------------------------------------------------------
cpu_policy: aws.autoscaling.Policy = aws.autoscaling.Policy(
    "app-asg-cpu50",
    autoscaling_group_name=asg.name,
    policy_type="TargetTrackingScaling",
    target_tracking_configuration=aws.autoscaling.PolicyTargetTrackingConfigurationArgs(
        predefined_metric_specification=aws.autoscaling.PolicyTargetTrackingConfigurationPredefinedMetricSpecificationArgs(
            predefined_metric_type="ASGAverageCPUUtilization",
        ),
        target_value=50.0,
        disable_scale_in=False,
    ),
    opts=pulumi.ResourceOptions(depends_on=[asg]),
)

# --------------------------------------------------------------------------------------
# 8b) Target Tracking por ALB RequestCount Per Target
#     Requiere resource_label con formato:
#     app/<alb-name>/<alb-id>/targetgroup/<tg-name>/<tg-id>
# --------------------------------------------------------------------------------------
def build_alb_tg_label(alb_arn: str, tg_arn: str) -> str:
    # Ejemplos:
    # alb ARN suffix: 'loadbalancer/app/app-alb-dc847ff/1583775791'
    # tg  ARN suffix: 'targetgroup/app-tg/1a2b3c4d5e6f7g8h'
    alb_suffix: str = alb_arn.split(":")[-1]              # 'loadbalancer/app/...'
    tg_suffix: str = tg_arn.split(":")[-1]                # 'targetgroup/...'
    alb_bits: List[str] = alb_suffix.split("/")
    tg_bits: List[str] = tg_suffix.split("/")
    # alb_bits: ['loadbalancer', 'app', '<alb-name>', '<alb-id>']
    # tg_bits : ['targetgroup', '<tg-name>', '<tg-id>']
    lb_type: str = alb_bits[1]            # 'app'
    alb_name: str = alb_bits[2]
    alb_id: str = alb_bits[3]
    tg_name: str = tg_bits[1]
    tg_id: str = tg_bits[2]
    return f"{lb_type}/{alb_name}/{alb_id}/targetgroup/{tg_name}/{tg_id}"

resource_label: Output[str] = Output.all(alb.arn, tg.arn).apply(
    lambda pair: build_alb_tg_label(pair[0], pair[1])
)

alb_req_policy: aws.autoscaling.Policy = aws.autoscaling.Policy(
    "app-asg-alb-req",
    autoscaling_group_name=asg.name,
    policy_type="TargetTrackingScaling",
    target_tracking_configuration=aws.autoscaling.PolicyTargetTrackingConfigurationArgs(
        predefined_metric_specification=aws.autoscaling.PolicyTargetTrackingConfigurationPredefinedMetricSpecificationArgs(
            predefined_metric_type="ALBRequestCountPerTarget",
            resource_label=resource_label,
        ),
        # Objetivo (aprox. req/seg por target). Ajusta luego para tu demo.
        target_value=60.0,
        disable_scale_in=False,
    ),
    opts=pulumi.ResourceOptions(depends_on=[asg]),
)

# --------------------------------------------------------------------------------------
# 9) Outputs
# --------------------------------------------------------------------------------------
pulumi.export("alb_dns_name", alb.dns_name)  # type: ignore[arg-type]
pulumi.export("asg_name", asg.name)          # type: ignore[arg-type]
