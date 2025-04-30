#!/usr/bin/env bash
set -e

BASE_URL="http://localhost:8080/api"

# helper for JSON endpoints
test_json() {
  local name=$1
  local param=$2
  local value=$3

  echo "=== $name (JSON) ==="
  echo "→ $param=$value"
  curl -s "${BASE_URL}?${param}=${value}" \
    | jq .
  echo
}

# helper for XML endpoints (using sed to break between tags)
test_xml() {
  local name=$1
  local param=$2
  local value=$3

  echo "=== $name (XML) ==="
  echo "→ $param=$value"
  curl -s -H "Accept: application/xml" \
       "${BASE_URL}?${param}=${value}" \
    | sed 's/></>\n</g'
  echo
}

echo "# Airport Temperature"
test_json "Airport Temp DEN"        queryAirportTemp DEN
test_xml  "Airport Temp LAX"        queryAirportTemp LAX

echo "# Stock / Futures Price"
test_json "S&P Futures (ES=F)"      queryStockPrice "ES=F"
test_xml  "S&P Futures (ES=F)"      queryStockPrice "ES=F"

echo "# Eval Expression"
test_json "Expression 6*7"          queryEval "6*7"
