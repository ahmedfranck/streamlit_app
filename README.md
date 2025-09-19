
# E‑Mobility Sales and Operations Dashboard (Streamlit)

This is a ready-to-run portfolio dashboard using Streamlit and Plotly with a synthetic dataset for e-mobility sales and operations.

## Quick start (local)

1. Install Python 3.10+
2. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

The app will open in your browser at http://localhost:8501

## Deploy to Streamlit Community Cloud

1. Push these files to a new GitHub repo
   - app.py
   - sales_ebus_sample.csv
   - requirements.txt
   - README.md
2. Go to https://share.streamlit.io, connect your GitHub, select the repo and app.py as the entry point, then deploy.

## How to use

- Use the filters on the left to slice the data by date, region, country, product, sales rep, channel, and segment.
- KPIs at the top update with your filters.
- Tabs show trends, product mix, geography and reps.
- Download the filtered dataset from the Data tab.

## Notes

- All data is synthetic and only for demonstration.
