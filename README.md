# Team AD Automations

This workspace contains a Streamlit app and starter document automation for generating offer letters in seconds.

## Streamlit app

Install requirements:

```bash
pip install -r requirements.txt
```

Run locally:

```bash
streamlit run app.py
```

The app includes:

- Google login through Streamlit OIDC
- Single offer letter generation
- Bulk CSV upload and ZIP download
- Utility slots for future tools

## Google login setup

Create `.streamlit/secrets.toml` from `.streamlit/secrets.example.toml`.

In Google Cloud, create an OAuth client and add these authorized redirect URIs:

- Local: `http://localhost:8501/oauth2callback`
- Production: `https://YOUR-APP-DOMAIN/oauth2callback`

Use the Google client ID and client secret in `.streamlit/secrets.toml` or in your hosting provider's Streamlit secrets.

For team access control, set one or both:

- `allowed_domains = ["yourcompany.com"]`
- `allowed_emails = ["person@yourcompany.com"]`

## Offer letter generator

The generator uses:

- `templates/offer_letter_template.docx` as the master Word template
- `data/offer_letters.csv` as the candidate input file
- `generated_docs/` as the output folder

Run:

```bash
/Users/rakeshpendem/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 generate_offer_letters.py
```

On macOS, you can also double-click `run_offer_letters.command`.

Each row in `data/offer_letters.csv` creates one offer letter.
Generated offer letters are ignored by Git so private candidate documents do not get pushed by accident.

## Adding a new candidate

Add another row to `data/offer_letters.csv` with these columns:

- `candidate_name`
- `role`
- `annual_salary`
- `offer_date`
- `company`
- `office_address`
- `signer_name`
- `signer_title`
- `responsibilities`

Separate multiple responsibilities with `|`.
