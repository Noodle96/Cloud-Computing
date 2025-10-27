#!/usr/bin/env bash
# termA.sh — Terminal A: sanidad, línea base, carga y balanceo (robusto con ARN)
set -euo pipefail

# Parámetros de carga (ajustables)
TOTAL_POR_RAFAGA="${TOTAL_POR_RAFAGA:-2000}"
CONCURRENCIA="${CONCURRENCIA:-50}"
NUM_RAFAGAS="${NUM_RAFAGAS:-10}"

banner() { echo; echo "========== $* =========="; }

banner "Cargando variables (env.sh)"
source ./env.sh

banner "Sanidad del ALB (deberías ver 'Hola desde ...')"
curl -s "${ALB}" | head -n1 || true

# ---------- Resolver ARNs de forma robusta ----------
banner "Resolviendo ARN del Load Balancer a partir del DNS"
LB_ARN="$(aws elbv2 describe-load-balancers \
  --profile "${PROFILE}" --region "${REGION}" \
  --query "LoadBalancers[?DNSName=='${ALB_HOST}'].LoadBalancerArn | [0]" \
  --output text)"
echo "[termA] LB_ARN=${LB_ARN}"

if [[ -z "${LB_ARN}" || "${LB_ARN}" == "None" ]]; then
  echo "[termA] ERROR: No pude resolver el LB_ARN desde el DNS ${ALB_HOST}." >&2
  exit 1
fi

banner "Resolviendo Target Group ARN asociado al ALB"
# Más robusto: lee el TG directamente desde el ALB (sin depender del nombre)
TG_ARN="$(aws elbv2 describe-target-groups \
  --load-balancer-arn "${LB_ARN}" \
  --profile "${PROFILE}" --region "${REGION}" \
  --query 'TargetGroups[0].TargetGroupArn' --output text)"
echo "[termA] TG_ARN=${TG_ARN}"

if [[ -z "${TG_ARN}" || "${TG_ARN}" == "None" ]]; then
  echo "[termA] ERROR: No pude resolver el Target Group del ALB." >&2
  exit 1
fi

# (Opcional) si necesitas el Listener ARN en algún punto:
# LISTENER_ARN="$(aws elbv2 describe-listeners \
#   --load-balancer-arn "${LB_ARN}" \
#   --profile "${PROFILE}" --region "${REGION}" \
#   --query 'Listeners[?DefaultActions[0].TargetGroupArn!=`null`][0].ListenerArn' --output text)"
# echo "[termA] LISTENER_ARN=${LISTENER_ARN}"

banner "Línea base: estado del ASG"
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names "${ASG_NAME}" \
  --profile "${PROFILE}" --region "${REGION}" \
  --query 'AutoScalingGroups[0].{Desired:DesiredCapacity,All:length(Instances),Instances:Instances[*].{Id:InstanceId,State:LifecycleState}}'

banner "Línea base: salud de targets del Target Group"
aws elbv2 describe-target-health \
  --target-group-arn "${TG_ARN}" \
  --profile "${PROFILE}" --region "${REGION}" \
  --query 'TargetHealthDescriptions[*].{Id:Target.Id,State:TargetHealth.State,Reason:TargetHealth.Reason}'

read -rp $'\n[termA] Presiona ENTER para iniciar la CARGA concurrente...' _

banner "Generando CARGA: ${NUM_RAFAGAS} ráfagas x ${TOTAL_POR_RAFAGA} req, concurrencia ${CONCURRENCIA}"
for b in $(seq 1 "${NUM_RAFAGAS}"); do
  echo "[termA] Ráfaga ${b}/${NUM_RAFAGAS}..."
  seq "${TOTAL_POR_RAFAGA}" | xargs -I{} -P "${CONCURRENCIA}" curl -s -o /dev/null "${ALB}"
done
echo "[termA] Carga finalizada. Espera ~1–3 min para que CloudWatch alimente la política."

banner "Balanceo actual (hostnames únicos en respuestas)"
for i in {1..15}; do
  curl -s "${ALB}" | sed -n 's/.*Hola desde \(.*\)<.*/\1/p'
done | sort | uniq -c

echo
echo "[termA] Sugerencia: observa en la Terminal B cómo sube Desired/All/InService."
