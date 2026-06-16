#!/usr/bin/env bash
# Smoke-test all Amoozeshyar API endpoints via curl.
# Usage: ./scripts/smoke_test_api.sh [BASE_URL]
# Requires: curl, python3, running Django server (default http://127.0.0.1:8000)

set -uo pipefail

BASE_URL="${1:-http://127.0.0.1:8000}"
API="${BASE_URL}/api/v1"
PASS=0
FAIL=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() {
  PASS=$((PASS + 1))
  echo -e "${GREEN}PASS${NC} $1"
}

fail() {
  FAIL=$((FAIL + 1))
  echo -e "${RED}FAIL${NC} $1"
  [[ -n "${2:-}" ]] && echo "       $2"
}

# curl without cookies — token auth only
curl_api() {
  curl -s -w "\n__HTTP_CODE__:%{http_code}" \
    --cookie "" \
    "$@"
}

http_code() {
  echo "$1" | sed -n 's/.*__HTTP_CODE__:\([0-9]*\)$/\1/p'
}

body_only() {
  echo "$1" | sed '/__HTTP_CODE__:/d'
}

json_field() {
  body_only "$1" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d$2)" 2>/dev/null || echo ""
}

login_token() {
  local user="$1" pass="$2"
  local resp
  resp=$(curl_api -X POST "${API}/auth/login/" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${user}\",\"password\":\"${pass}\"}")
  local code
  code=$(http_code "$resp")
  if [[ "$code" != "200" ]]; then
    echo ""
    return 1
  fi
  json_field "$resp" "['token']"
}

expect_code() {
  local label="$1" expected="$2" actual="$3" resp="${4:-}"
  if [[ "$actual" == "$expected" ]]; then
    pass "$label (HTTP $actual)"
  else
    fail "$label" "expected HTTP $expected, got $actual — $(body_only "$resp" | head -c 120)"
  fi
}

expect_code_in() {
  local label="$1" actual="$2" resp="${3:-}"
  shift 3
  for exp in "$@"; do
    if [[ "$actual" == "$exp" ]]; then
      pass "$label (HTTP $actual)"
      return
    fi
  done
  fail "$label" "expected one of [$*], got $actual — $(body_only "$resp" | head -c 120)"
}

echo "=== Amoozeshyar API Smoke Test ==="
echo "Base URL: ${BASE_URL}"
echo ""

# --- Phase A: Public ---
echo "--- Phase A: Public endpoints ---"

resp=$(curl_api "${BASE_URL}/api/ping/")
expect_code "GET /api/ping/" "200" "$(http_code "$resp")" "$resp"

resp=$(curl_api -X POST "${API}/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_student","password":"demo1234"}')
code=$(http_code "$resp")
STUDENT_TOKEN=$(json_field "$resp" "['token']")
if [[ "$code" == "200" && -n "$STUDENT_TOKEN" ]]; then
  pass "POST /auth/login/ valid credentials (HTTP 200 + token)"
else
  fail "POST /auth/login/ valid credentials" "HTTP $code — run: python manage.py seed_api_demo"
  echo ""
  echo -e "${YELLOW}Cannot continue without demo_student. Run seeder first.${NC}"
  exit 1
fi

resp=$(curl_api -X POST "${API}/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_student","password":"wrongpass"}')
expect_code "POST /auth/login/ bad password" "401" "$(http_code "$resp")" "$resp"

resp=$(curl_api -X POST "${API}/auth/password/reset/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_student","security_answer":"wrong","new_password":"newpass1234"}')
expect_code_in "POST /auth/password/reset/ wrong answer" "$(http_code "$resp")" "$resp" "400"

resp=$(curl_api -X POST "${API}/auth/password/reset/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_student","security_answer":"tehran","new_password":"demo1234"}')
expect_code_in "POST /auth/password/reset/ correct answer" "$(http_code "$resp")" "$resp" "200"

# Re-login after password reset (still demo1234)
STUDENT_TOKEN=$(login_token "demo_student" "demo1234")
if [[ -z "$STUDENT_TOKEN" ]]; then
  fail "Re-login after password reset" "could not obtain token"
else
  pass "Re-login after password reset"
fi

ADMIN_TOKEN=$(login_token "demo_admin" "demo1234")
if [[ -n "$ADMIN_TOKEN" ]]; then
  pass "Login demo_admin"
else
  fail "Login demo_admin" "could not obtain token"
fi

echo ""
echo "--- Phase B: Auth enforcement ---"

resp=$(curl_api "${API}/auth/me/")
expect_code "GET /auth/me/ no auth" "401" "$(http_code "$resp")" "$resp"

resp=$(curl_api "${API}/auth/me/" -H "Authorization: fake_key")
code=$(http_code "$resp")
body=$(body_only "$resp")
if [[ "$code" == "401" ]] && echo "$body" | grep -q "Token"; then
  pass "GET /auth/me/ invalid Authorization format (HTTP 401)"
else
  fail "GET /auth/me/ invalid Authorization format" "HTTP $code — $(echo "$body" | head -c 120)"
fi

resp=$(curl_api "${API}/auth/me/" -H "Authorization: Token ${STUDENT_TOKEN}")
expect_code "GET /auth/me/ valid token" "200" "$(http_code "$resp")" "$resp"

echo ""
echo "--- Phase C: Role matrix ---"

# Student composite pages
COMPOSITE_PAGES=(
  "pages/dashboard/"
  "pages/semester-transcript/"
  "pages/full-transcript/"
  "pages/grades/"
  "pages/course-selection/"
  "pages/add-drop/"
  "pages/financial/"
  "pages/payment-history/"
  "pages/loan-request/"
  "pages/student-requests/"
  "pages/leave-request/"
  "pages/teachers/"
  "pages/grade-objection/"
)

for page in "${COMPOSITE_PAGES[@]}"; do
  resp=$(curl_api "${API}/${page}" -H "Authorization: Token ${STUDENT_TOKEN}")
  expect_code "GET /${page} (student)" "200" "$(http_code "$resp")" "$resp"
done

resp=$(curl_api "${API}/persons/" -H "Authorization: Token ${STUDENT_TOKEN}")
expect_code "GET /persons/ (student denied)" "403" "$(http_code "$resp")" "$resp"

resp=$(curl_api "${API}/students/" -H "Authorization: Token ${STUDENT_TOKEN}")
expect_code "GET /students/ (student allowed)" "200" "$(http_code "$resp")" "$resp"

if [[ -n "$ADMIN_TOKEN" ]]; then
  resp=$(curl_api "${API}/auth-accounts/" -H "Authorization: Token ${ADMIN_TOKEN}")
  expect_code "GET /auth-accounts/ (admin)" "200" "$(http_code "$resp")" "$resp"

  resp=$(curl_api "${API}/persons/" -H "Authorization: Token ${ADMIN_TOKEN}")
  expect_code "GET /persons/ (admin)" "200" "$(http_code "$resp")" "$resp"
fi

resp=$(curl_api -X POST "${API}/departments/" \
  -H "Authorization: Token ${STUDENT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"department_code":"X","department_title":"Test"}')
expect_code "POST /departments/ (student denied)" "403" "$(http_code "$resp")" "$resp"

if [[ -n "$ADMIN_TOKEN" ]]; then
  SMOKE_DEPT="SMK$(date +%s)"
  resp=$(curl_api -X POST "${API}/departments/" \
    -H "Authorization: Token ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"department_code\":\"${SMOKE_DEPT}\",\"department_title\":\"Smoke Test Dept\"}")
  expect_code_in "POST /departments/ (admin)" "$(http_code "$resp")" "$resp" "201" "200"
fi

echo ""
echo "--- Phase D: CRUD list smoke (student GET) ---"

ROUTER_ENDPOINTS=(
  const-values departments education-branches tendencies terms
  persons phone-numbers email-addresses person-skills postal-addresses
  teachers teacher-research-interests students employees
  lessons classes class-offers exams exam-invigilators exam-results
  attendances transcripts teacher-evaluations prerequisite-warnings
  student-payments student-requests academic-leave-requests scholarships
  dormitory-requests loans
  books library-book-lendings library-reserves companies internships
  document-students academic-programs academic-events academic-announcements
  auth-roles auth-accounts auth-sessions auth-account-roles
)

STUDENT_SCOPED=(
  student-payments transcripts exam-results attendances
  teacher-evaluations prerequisite-warnings library-book-lendings
  internships document-students academic-leave-requests scholarships
  dormitory-requests student-requests
)

for ep in "${ROUTER_ENDPOINTS[@]}"; do
  resp=$(curl_api "${API}/${ep}/" -H "Authorization: Token ${STUDENT_TOKEN}")
  code=$(http_code "$resp")
  body=$(body_only "$resp")

  if [[ "$code" == "500" ]]; then
    fail "GET /${ep}/" "HTTP 500 server error"
    continue
  fi

  case "$ep" in
    persons|auth-roles|auth-accounts|auth-sessions|auth-account-roles)
      if [[ "$code" == "403" ]]; then
        pass "GET /${ep}/ (student denied, HTTP 403)"
      else
        fail "GET /${ep}/ (student should be denied)" "HTTP $code"
      fi
      ;;
    *)
      if [[ "$code" == "200" ]]; then
        pass "GET /${ep}/ (HTTP 200)"
        for scoped in "${STUDENT_SCOPED[@]}"; do
          if [[ "$ep" == "$scoped" ]]; then
            count=$(echo "$body" | python3 -c "
import sys, json
d = json.load(sys.stdin)
results = d.get('results', d if isinstance(d, list) else [])
print(len(results) if isinstance(results, list) else 0)
" 2>/dev/null || echo "0")
            if [[ "${count:-0}" -ge 1 ]]; then
              pass "GET /${ep}/ has seeded data (count=$count)"
            else
              fail "GET /${ep}/ seeded data" "expected count >= 1, got ${count:-0}"
            fi
            break
          fi
        done
      else
        fail "GET /${ep}/" "HTTP $code — $(echo "$body" | head -c 80)"
      fi
      ;;
  esac
done

echo ""
echo "--- Phase E: Error cases ---"

resp=$(curl_api "${API}/students/999999/" -H "Authorization: Token ${STUDENT_TOKEN}")
expect_code "GET /students/999999/" "404" "$(http_code "$resp")" "$resp"

resp=$(curl_api -X POST "${API}/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_student"}')
expect_code "POST /auth/login/ missing password" "400" "$(http_code "$resp")" "$resp"

resp=$(curl_api "${API}/auth/me/" -H "Authorization: Token invalidtoken000")
code=$(http_code "$resp")
body=$(body_only "$resp")
if [[ "$code" == "401" ]] && echo "$body" | grep -q "detail"; then
  pass "GET /auth/me/ invalid token (HTTP 401)"
else
  fail "GET /auth/me/ invalid token" "HTTP $code — $(echo "$body" | head -c 80)"
fi

echo ""
echo "--- Phase F: Admin on student-only pages + grade objection data ---"

if [[ -n "$ADMIN_TOKEN" ]]; then
  for page in pages/dashboard/ pages/financial/ pages/course-selection/ pages/grade-objection/; do
    resp=$(curl_api "${API}/${page}" -H "Authorization: Token ${ADMIN_TOKEN}")
    expect_code "GET /${page} (admin, no student profile)" "404" "$(http_code "$resp")" "$resp"
  done
fi

resp=$(curl_api "${API}/pages/grade-objection/" -H "Authorization: Token ${STUDENT_TOKEN}")
body=$(body_only "$resp")
objection_count=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('objections',[])))" 2>/dev/null || echo "0")
if [[ "$(http_code "$resp")" == "200" && "${objection_count:-0}" -ge 1 ]]; then
  pass "GET /pages/grade-objection/ has seeded objections (count=$objection_count)"
else
  fail "GET /pages/grade-objection/ seeded objections" "HTTP $(http_code "$resp"), count=${objection_count:-0}"
fi

resp=$(curl_api "${API}/loans/" -H "Authorization: Token ${STUDENT_TOKEN}")
loan_count=$(body_only "$resp" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('results',[])))" 2>/dev/null || echo "0")
if [[ "$(http_code "$resp")" == "200" && "${loan_count:-0}" -ge 1 ]]; then
  pass "GET /loans/ scoped for student (count=$loan_count)"
else
  fail "GET /loans/ scoped for student" "HTTP $(http_code "$resp"), count=${loan_count:-0}"
fi

echo ""
echo "=== Summary ==="
echo -e "Passed: ${GREEN}${PASS}${NC}  Failed: ${RED}${FAIL}${NC}"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
exit 0
