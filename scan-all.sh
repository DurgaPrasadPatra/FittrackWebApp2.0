#!/bin/bash
# Scans every image used by this docker-compose project with Trivy.
# Discovers image names automatically — no hardcoding needed.

REPORT_DIR="trivy-reports/$(date +%F)"
mkdir -p "$REPORT_DIR"

echo "=================================================="
echo " FitTrack Trivy Scan — $(date)"
echo "=================================================="

# Ask Compose itself which images this project actually uses —
# this is the config-driven way, works even if images get renamed later
IMAGES=$(docker compose config --images)

if [ -z "$IMAGES" ]; then
  echo "No images found. Is docker-compose.yaml in this folder?"
  exit 1
fi

echo "Found images:"
echo "$IMAGES"
echo ""

for IMAGE in $IMAGES; do
  SAFE_NAME=$(echo "$IMAGE" | tr '/:' '__')
  REPORT_FILE="$REPORT_DIR/${SAFE_NAME}.txt"

  echo "--- Scanning $IMAGE ---"
  trivy image \
    --severity HIGH,CRITICAL \
    --exit-code 0 \
    --format table \
    "$IMAGE" | tee "$REPORT_FILE"

  echo "Report saved: $REPORT_FILE"
  echo ""
done

echo "=================================================="
echo " All scans complete. Reports in: $REPORT_DIR"
echo "=================================================="
