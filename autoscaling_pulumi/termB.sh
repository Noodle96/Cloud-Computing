#!/usr/bin/env bash
# termB.sh — Terminal B: monitor del Auto Scaling Group
set -euo pipefail

banner() { echo; echo "========== $* =========="; }

banner "Cargando variables (env.sh)"
source ./env.sh

banner "Monitor del ASG (Desired / InService / All) — Ctrl+C para salir"
while true; do
  date
  aws autoscaling describe-auto-scaling-groups \
    --auto-scaling-group-names "${ASG_NAME}" \
    --profile "${PROFILE}" --region "${REGION}" \
    --query 'AutoScalingGroups[0].{Desired:DesiredCapacity,InService:length(Instances[?LifecycleState==`InService`]),All:length(Instances)}'
  sleep 20
done
