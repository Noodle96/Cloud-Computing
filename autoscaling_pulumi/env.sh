#!/usr/bin/env bash
# env.sh — Variables comunes para la demo de autoscaling
set -euo pipefail

: "${REGION:=us-east-1}"
: "${PROFILE:=academy}"

echo "[env] Verificando acceso a Pulumi..."
pulumi stack --non-interactive >/dev/null

echo "[env] Leyendo outputs del stack..."
ALB_DNS="$(pulumi stack output alb_dns_name)"
ASG_NAME="$(pulumi stack output asg_name)"

if [[ -z "${ALB_DNS}" || -z "${ASG_NAME}" ]]; then
  echo "[env] ERROR: No pude leer salidas de Pulumi (¿hiciste 'pulumi up'?)." >&2
  exit 1
fi

export REGION PROFILE
export ALB="http://${ALB_DNS}"
export ALB_HOST="${ALB_DNS}"
export ASG_NAME

cat <<EOF
[env] OK:
  REGION=${REGION}
  PROFILE=${PROFILE}
  ALB=${ALB}
  ASG_NAME=${ASG_NAME}
EOF
