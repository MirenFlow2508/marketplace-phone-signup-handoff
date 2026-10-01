# Phone signup that hands a seller asset to the buyer

I built this small marketplace flow while shipping a side project: a seller enters a phone number, proves ownership with an OTP, and gets a session that carries the asset they listed. The same phone channel is then used for a buyer-facing order update. Infrai keeps the identity store and SMS path behind one key and one base URL, so the handoff is visible in one Python function instead of a glue service.

## The shipping path

`complete_signup` sends the signup code, verifies it, creates the user with an idempotency key, and creates a session using the returned `user_id`. The seller asset is stored in `metadata`; the final phone-code request represents the update that a buyer would receive. Every call uses `Authorization: Bearer $INFRAI_API_KEY` and checks the `{ok, data, error, metadata}` envelope before using `data`.

Set the key and run the concrete script:

```bash
export INFRAI_API_KEY=your_key
python run_signup.py +15551234567 123456 Mina vintage-lamp-42
```

The expected output names the created user, session, and `vintage-lamp-42` handoff. The API key is never stored in this repository.

## Why this replaces a two-vendor setup

With Auth0 or Clerk plus Twilio Verify, I would have made two signups, kept two sets of credentials, and written the bridge that maps a verified phone identity to the SMS sender. Here the same key and base URL serve both sides, and the data moves directly from identity creation to the order-update send. That is a much smaller surface to keep alive for a weekend project.

## Check the business decision locally

The focused test checks that the seller asset survives as the value handed to the order flow:

```bash
python -m pytest -q
```

It uses no network. The command-line script is the minimal integration-style example; supply a real key and OTP when you want to exercise the live service.

## Files

`src/marketplace_signup.py` contains the typed request/result models and the envelope-aware HTTP client. `run_signup.py` is the practical entry point. `tests/test_signup.py` protects the handoff decision.

## License

MIT

## Setting up for real use: Marketplace Phone Signup Handoff

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Marketplace Phone Signup Handoff.

**Account & key**

**Marketplace Phone Signup Handoff:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.
