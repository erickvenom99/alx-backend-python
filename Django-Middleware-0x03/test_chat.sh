#!/bin/bash

# --- Configuration ---
API_BASE_URL="http://localhost:8000/api"
CONVERSATION_ID='2c86c4b5-1775-4696-b306-be93429dc857'

# !!! IMPORTANT: PASTE BOB'S LONG-LIVED REFRESH TOKEN HERE !!!
# This token usually lasts for days (as per your setting).
# Make sure to update this if you haven't yet!
BOB_REFRESH_TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2Mzc0NDk4NywiaWF0IjoxNzYzNjU4NTg3LCJqdGkiOiI2NzJlZmFkYTEwMzQ0ZTIzOWNmNzcyNmU2YzFiMjkwNSIsInVzZXJfaWQiOiIxOTRjMzllMS03NGIyLTRmZTQtOGQyYS01OTc1YTUyMTRmM2MifQ.ZQXDNbjiKT-V0YtMF64pQNRyq88o7X_kbNB8R0jxOMI' 

# --- Step 1: Request a NEW Access Token using the Refresh Token ---
echo "--- Step 1: Requesting fresh Access Token..."

# The refresh endpoint is at /api/token/refresh/
REFRESH_RESPONSE=$(curl -s -X POST \
  "${API_BASE_URL}/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"${BOB_REFRESH_TOKEN}\"}")

# Check for errors in the refresh response
if echo "$REFRESH_RESPONSE" | grep -q "code"; then
    echo "ERROR: Failed to refresh token."
    echo "Server Response: $REFRESH_RESPONSE"
    echo "Ensure your REFRESH_TOKEN is correct and has not expired (it should last 1 day)."
    exit 1
fi

# Use 'jq' to extract the new access token
NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.access')

if [ -z "$NEW_ACCESS_TOKEN" ] || [ "$NEW_ACCESS_TOKEN" == "null" ]; then
    echo "ERROR: Failed to extract new access token from the response."
    echo "Full Response: $REFRESH_RESPONSE"
    exit 1
fi

echo "Successfully received a new Access Token."

# --- Step 2: Use the FRESH Access Token to send the message ---
echo ""
echo "--- Step 2: Sending message with the fresh token to conversation $CONVERSATION_ID ---"
echo "Expected Result: SUCCESS (201 Created)"

# FIX: Changed 'text' to 'message_body' to match the Django serializer requirement.
curl -X POST \
  "${API_BASE_URL}/conversations/${CONVERSATION_ID}/messages/" \
  -H "Authorization: Bearer ${NEW_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message_body": "The token refresh workflow works! This message was sent successfully."
  }'

echo ""
echo "--------------------------------------------------------"