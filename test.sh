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
  curl -s "${BASE_URL}?${param}=${value}" | jq .
  echo
}

# helper for XML endpoints
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

echo "# Airport Temperature Tests"
test_json "PRG (Prague)"       queryAirportTemp PRG
test_json "LAX (Los Angeles)"  queryAirportTemp LAX
test_xml  "JFK (New York)"     queryAirportTemp JFK

echo "# Stock Price Tests"
test_json "WFC (Wells Fargo)"   queryStockPrice WFC
test_json "AAPL (Apple)"        queryStockPrice AAPL
test_xml  "MSFT (Microsoft)"    queryStockPrice MSFT

echo "# Eval Expression Tests"
test_json "1+2*3"               queryEval "1+2*3"
test_json "(10-2)/4"            queryEval "(10-2)/4"
test_xml  "2*(3+4)-5"           queryEval "2*(3+4)-5"
