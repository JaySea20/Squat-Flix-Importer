#!/bin/bash

# Endpoint URL
ENDPOINT="https://squatflix.jaysea20.net/webhook/autobrr"

# Payload JSON
read -r -d '' PAYLOAD <<EOF
{
  "releaseName": "Some.Movie.2025.1080p.WEB-DL",
  "indexer": "AwesomeIndexer",
  "filterName": "Squat-Flix Trigger",
  "protocol": "Torrent",
  "downloadType": "Internal",
  "imdbId": "tt1234567",
  "size": 2147483648,
  "timestamp": "2025-10-02T08:47:00Z"
}
EOF

# Send POST request
echo "Sending test payload to $ENDPOINT..."
curl -X POST "$ENDPOINT" \
     -H "Content-Type: application/json" \
     -d "$PAYLOAD"

echo -e "\nDone."
