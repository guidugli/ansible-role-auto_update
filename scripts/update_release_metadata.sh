#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="python3"
SKIP_UPDATE_MATRIX="false"
VARS_FILE="${REPO_ROOT}/molecule/shared/vars.yml"
TEMPLATE_FILE="${REPO_ROOT}/templates/meta_main.yml.j2"
OUTPUT_FILE="${REPO_ROOT}/meta/main.yml"
VERBOSE="false"

log() {
  printf '%s
' "$*"
}

err() {
  printf 'ERROR: %s
' "$*" >&2
}

usage() {
  cat <<'EOF'
Usage:
  ./scripts/update_release_metadata.sh [options]

Options:
  --python <path>           Python interpreter to use (default: python3)
  --skip-update-matrix      Do not refresh molecule/shared/vars.yml before rendering
  --vars-file <path>        Shared vars file to use (default: molecule/shared/vars.yml)
  --template <path>         Metadata template to use (default: templates/meta_main.yml.j2)
  --output <path>           Output file to write (default: meta/main.yml)
  --verbose                 Enable shell tracing
  -h, --help                Show this help text

Behavior:
  1) Optionally refreshes molecule/shared/vars.yml via scripts/update_matrix.py
  2) Syntax-checks generator scripts before executing them
  3) Renders Molecule inventories from shared vars
  4) Renders meta/main.yml from templates/meta_main.yml.j2
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --skip-update-matrix)
      SKIP_UPDATE_MATRIX="true"
      shift
      ;;
    --vars-file)
      VARS_FILE="$2"
      shift 2
      ;;
    --template)
      TEMPLATE_FILE="$2"
      shift 2
      ;;
    --output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    --verbose)
      VERBOSE="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      err "Unknown argument: $1"
      exit 2
      ;;
  esac
done

if [[ "$VERBOSE" == "true" ]]; then
  set -x
fi

command -v "$PYTHON_BIN" >/dev/null 2>&1 || {
  err "Python interpreter not found: $PYTHON_BIN"
  exit 3
}

UPDATE_MATRIX_SCRIPT="${REPO_ROOT}/scripts/update_matrix.py"
RENDER_META_SCRIPT="${REPO_ROOT}/scripts/render_meta_main.py"
RENDER_INVENTORY_SCRIPT="${REPO_ROOT}/scripts/render_inventory.py"

[[ -f "$RENDER_META_SCRIPT" ]] || {
  err "Renderer script not found: $RENDER_META_SCRIPT"
  exit 4
}

[[ -f "$RENDER_INVENTORY_SCRIPT" ]] || {
  err "Inventory renderer script not found: $RENDER_INVENTORY_SCRIPT"
  exit 5
}

log '==> Syntax-checking generator scripts'
"$PYTHON_BIN" -m py_compile "$RENDER_META_SCRIPT"
"$PYTHON_BIN" -m py_compile "$RENDER_INVENTORY_SCRIPT"

if [[ "$SKIP_UPDATE_MATRIX" != "true" ]]; then
  [[ -f "$UPDATE_MATRIX_SCRIPT" ]] || {
    err "Matrix update script not found: $UPDATE_MATRIX_SCRIPT"
    exit 6
  }
  "$PYTHON_BIN" -m py_compile "$UPDATE_MATRIX_SCRIPT"
  log '==> Refreshing Molecule matrix'
  (cd "$REPO_ROOT" && "$PYTHON_BIN" "$UPDATE_MATRIX_SCRIPT")
else
  log '==> Skipping matrix refresh (requested)'
fi

[[ -f "$VARS_FILE" ]] || {
  err "Shared vars file not found: $VARS_FILE"
  exit 7
}

[[ -f "$TEMPLATE_FILE" ]] || {
  err "Template file not found: $TEMPLATE_FILE"
  exit 8
}

mkdir -p "$(dirname -- "$OUTPUT_FILE")"

log '==> Rendering Molecule inventories from shared matrix'
(cd "$REPO_ROOT" && "$PYTHON_BIN" "$RENDER_INVENTORY_SCRIPT")

log '==> Rendering meta/main.yml from shared matrix'
(cd "$REPO_ROOT" && "$PYTHON_BIN" "$RENDER_META_SCRIPT"   --vars-file "$VARS_FILE"   --template "$TEMPLATE_FILE"   --output "$OUTPUT_FILE")

log '==> Done'
log "Shared vars : $VARS_FILE"
log "Template    : $TEMPLATE_FILE"
log "Output      : $OUTPUT_FILE"
log ''
log 'Suggested next steps:'
log '  1) git diff -- meta/main.yml molecule/'
log '  2) molecule test -s default'
log '  3) Commit if everything looks good'
