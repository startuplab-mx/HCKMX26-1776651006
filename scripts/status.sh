#!/usr/bin/env bash
# Nahual ops one-liner — print everything you need to know about the
# system in <5s. Calls the public /admin/runtime-info endpoint and
# formats it for a terminal.
#
# Usage:
#   ./scripts/status.sh                 # default: production
#   NAHUAL_API=http://localhost:8000 ./scripts/status.sh   # local

set -euo pipefail

API="${NAHUAL_API:-http://159.223.187.6}"

echo "════════════════════════════════════════════════════════════"
echo "  🛡️  NAHUAL · status report · $(date '+%Y-%m-%d %H:%M:%S')"
echo "  $API"
echo "════════════════════════════════════════════════════════════"

# Fast health
echo
echo "── /health ──"
curl -sf -m 5 "$API/health" | python3 -m json.tool 2>/dev/null \
  || echo "  ⚠️  unreachable"

# Aggregate /admin/runtime-info (single round-trip).
# Use a heredoc with single quotes so $ stays literal in Python.
echo
echo "── /admin/runtime-info ──"
RAW="$(curl -sf -m 8 "$API/admin/runtime-info" || echo '{}')"
RAW="$RAW" python3 - <<'PY'
import os, json
try:
    r = json.loads(os.environ.get("RAW", "{}"))
except Exception:
    print("  ⚠️  invalid JSON"); raise SystemExit

v = r.get("version") or {}
d = r.get("dataset") or {}
b = r.get("bayesian") or {}
m = r.get("metrics") or {}

ver = "{:>10}".format(v.get("commit", "?"))
print("  version    {0}  branch={1}  env={2}".format(
    ver, v.get("branch", "?"), v.get("environment", "?")))
phases = d.get("phases") or {}
phases_str = "  ".join("{}:{}".format(k, v) for k, v in phases.items())
print("  dataset    {:>10}  [{}]".format(d.get("total_patterns", 0), phases_str))

if b:
    classes = b.get("classes") or {}
    classes_str = "  ".join("{}:{}".format(k, v) for k, v in classes.items())
    print("  bayesian   {:>10}  vocab={}  [{}]".format(
        b.get("total_docs", 0), b.get("vocab", 0), classes_str))

print("  uptime     {:>10}s  recent_alerts={}".format(
    m.get("uptime_seconds", 0),
    "yes" if r.get("recent_alerts") else "no"))
print("  requests   total={}  analyze={}  alert={}  transcribe={}  ocr={}".format(
    m.get("requests_total", 0),
    m.get("analyze_total", 0),
    m.get("alert_total", 0),
    m.get("transcribe_total", 0),
    m.get("ocr_total", 0)))

print()
print("  recent alerts:")
for a in (r.get("recent_alerts") or [])[:5]:
    ovr = " OVR" if a.get("override") else "    "
    lvl = "{:>8}".format(a.get("risk_level", "?"))
    plat = "{:>10}".format(a.get("platform", "?"))
    print("    #{:>3}  [{}{}]  {}  {}".format(
        a.get("id", "?"), lvl, ovr, plat, a.get("created_at", "?")))
PY

# Deep healthcheck (~6s) — DB + Anthropic + Groq.
echo
echo "── /admin/healthcheck-deep ──"
DEEP="$(curl -sf -m 12 "$API/admin/healthcheck-deep" || echo '{}')"
DEEP="$DEEP" python3 - <<'PY'
import os, json
try:
    r = json.loads(os.environ.get("DEEP", "{}"))
except Exception:
    print("  ⚠️  unreachable / invalid"); raise SystemExit
print("  all_ok: {}".format(r.get("all_ok")))
for k, v in (r.get("checks") or {}).items():
    icon = "✓" if v.get("ok") else "✗"
    detail = v.get("error") or v.get("reason") or v.get("status") or "ok"
    print("    {} {:>10s}  {}".format(icon, k, detail))
PY

echo
echo "════════════════════════════════════════════════════════════"
