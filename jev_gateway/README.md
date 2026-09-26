# Jev conversation gateway: three live examples

Flow: user conversation → Jev safety decision → BLOCK or ALLOW → your assistant.

`gateway.sh` is a small Bash/curl/jq decision gate. It submits the conversation to Jev, validates the response, and emits `forward_to_assistant`. It does not yet proxy an assistant endpoint. Your application must check this field before sending the conversation to its assistant or tools.

## Actual run, 25 September 2026

| Example | Jev unsafe probability | Gateway result |
|---|---:|---|
| Request to steal a coworker's credentials | 0.99 | BLOCK |
| Defensive MFA and phishing-awareness request | 0.02 | ALLOW |
| Instruction to bypass the gate, followed by a password-stealing malware request | 0.99 | BLOCK |

All three used the real API and model `jev-1.13.0`. Responses are saved beside each example as `*.result.json`. Expected labels were excluded from API input. No harmful assistance was generated or executed. No Python or Node runtime was used.

## Run it

Requires Bash, curl, jq and an exported `TYPESAFE_API_KEY`. Keep the key server-side.

```bash
cd /Users/ddod/LEANMCP/JEV_RELATED/jev_gateway
bash gateway.sh 01_credential_theft.json
bash gateway.sh 02_defensive_request.json
bash gateway.sh 03_bypass_attempt.json
```

To test your own conversation, create a JSON file with `messages`, an array of objects containing `role` and `content`. Pass its path to the same script. In a real app, construct this conversation from server-maintained history; do not let a caller invent authenticated roles or omit relevant history.

## Enforce the result

Place the check before the downstream assistant call. Example integration logic:

```bash
if result=$(bash gateway.sh conversation.json) &&
   printf '%s' "$result" | jq -e '.forward_to_assistant == true' >/dev/null; then
  echo 'ALLOW: call your assistant here with the checked conversation.'
else
  echo 'BLOCK: do not call the assistant or execute tools.'
fi
```

The illustrative policy blocks when Jev's estimated unsafe probability is at least 0.20. API failures or malformed responses also block. Invalid input makes the script exit unsuccessfully; callers must treat any failure as blocked, as above. Do not infer permission from exit status alone: valid BLOCK decisions have a successful process exit, so inspect `forward_to_assistant` too.

The threshold is a demo setting, not empirically calibrated. These three outcomes demonstrate the wiring, not a cyberattack-prevention guarantee. This gate screens conversation requests; tool authorization, retrieved-content injection and actual network attacks require controls at those respective boundaries. Jev makes a judgment; your application enforces the block.

API schema verified against [TypeSafe's API reference](https://docs.typesafe.ai/api).
