#!/bin/bash
# Step 3: Bob retrieves the conversation messages

# --- Configuration ---
# Bob's token: He should be able to view messages in a conversation he belongs to.
BOB="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYzNjY4MzU1LCJpYXQiOjE3NjM2Mzk1NTUsImp0aSI6ImMyODc1NWQ4ZTIxOTQzNWU4ZjNiMWUzMTg5NzI5MmEzIiwidXNlcl9pZCI6IjY5YTk5MDM0LTM5ZjUtNDA0Yi04MTEyLTFjZGFmZWEwYzJmOCJ9.jS62hB8b_Y5lQyV8uR4Z5MhX-gQ9vF7T4tS2nL_qA04"
BASE_URL="http://127.0.0.1:8000/api"

# !!! REPLACE THIS WITH THE ID FROM STEP 1 & 2 !!!
CONV_ID="2c86c4b5-1775-4696-b306-be93429dc857"

if [ "$CONV_ID" =="2c86c4b5-1775-4696-b306-be93429dc857" ]; then
    echo "ERROR: Please ensure CONV_ID is set correctly from Step 1."
    exit 1
fi

echo "3. Bob lists all messages in conversation $CONV_ID"
BOB_LIST_RESPONSE=$(curl -s -X GET $BASE_URL/conversations/$CONV_ID/messages/ \
    -H "Authorization: Bearer $BOB")

if echo "$BOB_LIST_RESPONSE" | jq . > /dev/null 2>&1; then
    echo "SUCCESS! Response (JSON):"
    echo "$BOB_LIST_RESPONSE" | jq .
    # The output should be a list containing the message Alice just sent.
else
    echo "ERROR: jq failed to parse Bob's list response (might be HTML traceback). RAW RESPONSE:"
    echo "$BOB_LIST_RESPONSE"
fi