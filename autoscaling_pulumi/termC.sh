#!/usr/bin/env bash
# termC.sh — Terminal C: métricas ALB (CloudWatch) y salud de targets (robusto con ARN)
set -euo pipefail

banner() { echo; echo "========== $* =========="; }

banner "Cargando variables (env.sh)"
source ./env.sh

banner "Resolviendo ARN del ALB desde el DNS"
LB_ARN="$(aws elbv2 describe-load-balancers \
  --profile "${PROFILE}" --region "${REGION}" \
  --query "LoadBalancers[?DNSName=='${ALB_HOST}'].LoadBalancerArn | [0]" \
  --output text)"
echo "[termC] LB_ARN=${LB_ARN}"

if [[ -z "${LB_ARN}" || "${LB_ARN}" == "None" ]]; then
  echo "[termC] ERROR: No pude resolver el LB_ARN desde el DNS ${ALB_HOST}." >&2
  exit 1
fi

banner "Resolviendo Target Group ARN asociado"
TG_ARN="$(aws elbv2 describe-target-groups \
  --load-balancer-arn "${LB_ARN}" \
  --profile "${PROFILE}" --region "${REGION}" \
  --query 'TargetGroups[0].TargetGroupArn' --output text)"
echo "[termC] TG_ARN=${TG_ARN}"

if [[ -z "${TG_ARN}" || "${TG_ARN}" == "None" ]]; then
  echo "[termC] ERROR: No pude resolver el TG_ARN desde el ALB." >&2
  exit 1
fi

banner "Construyendo dimensiones CloudWatch"
LB_DIM="$(echo "${LB_ARN}" | awk -F'loadbalancer/' '{print $2}')"
TG_DIM="$(echo "${TG_ARN}" | awk -F'targetgroup/' '{print "targetgroup/"$2}')"
cat <<EOF
[termC] Dimensiones:
  LoadBalancer = ${LB_DIM}
  TargetGroup  = ${TG_DIM}
EOF

banner "RequestCountPerTarget (últimos 15 min, por minuto)"
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name RequestCountPerTarget \
  --dimensions Name=LoadBalancer,Value="${LB_DIM}" Name=TargetGroup,Value="${TG_DIM}" \
  --start-time "$(date -u -d '15 minutes ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-15M +%Y-%m-%dT%H:%M:%SZ)" \
  --end-time   "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --period 60 \
  --statistics Sum \
  --profile "${PROFILE}" --region "${REGION}" \
  --query 'Datapoints | sort_by(@, &Timestamp)[].[Timestamp,Sum]' \
  --output table

banner "Salud de targets actuales"
aws elbv2 describe-target-health \
  --target-group-arn "${TG_ARN}" \
  --profile "${PROFILE}" --region "${REGION}" \
  --query 'TargetHealthDescriptions[*].{Id:Target.Id,State:TargetHealth.State,Reason:TargetHealth.Reason}'
