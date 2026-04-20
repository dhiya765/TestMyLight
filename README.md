# ATR-FTIR Algae Workshop App

This is a Streamlit prototype for your workshop. It uses the uploaded `PreparedDatasetATRFTIR.xlsx` workbook and provides:
- dataset explorer
- interactive spectral overlay plotting
- guided interpretation form
- classification form
- instructor dashboard

## Current storage behavior
By default, the app stores responses locally in:
- `data/responses_local.csv`
- `data/progress_local.csv`

That means you can test everything immediately without Google Sheets.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Switch to Google Sheets later
Create `.streamlit/secrets.toml` with something like:

```toml
storage_backend = "gsheets"

[connections.gsheets]
type = "gsheets"
spreadsheet = "YOUR_GOOGLE_SHEET_NAME_OR_URL"

[gsheets]
placeholder = true
```

You will also need the Streamlit Google Sheets connection configured with the service-account credentials expected by the connector.

## Recommended Google Sheet tabs
Create two worksheets:
- `responses`
- `progress`

## Notes
- The app automatically detects sheets with metadata rows at the top, such as binary, tertiary, quaternary, and algae-mixture datasets.
- The plotting page reverses the x-axis, which is typical for FTIR display.
- The instructor dashboard is wired to the same backend as the student pages.
