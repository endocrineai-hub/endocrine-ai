# Data Sources for This Project

## Confirmed Sources
- UCI Thyroid Disease
  - https://archive.ics.uci.edu/ml/datasets/Thyroid%2BDisease
- UCI Early Stage Diabetes Risk Prediction
  - https://archive.ics.uci.edu/dataset/529/early+stage+diabetes+risk+prediction+dataset
- UCI Diabetes 130-US Hospitals for years 1999-2008
  - https://archive.ics.uci.edu/dataset/296/diabetes%2B130-us%2Bhospitals%2Bfor%2Bye
- CDC NHANES
  - https://www.cdc.gov/nchs/nhanes/index.html
- PhysioNet MIMIC-IV
  - https://physionet.org/content/mimiciv/

## Local Data You Have
Add your own database export into:
- `ml/data/raw/local_db_export.csv`

Or keep it in SQLite and run the extractor:
- `python3 scripts/prepare_dataset.py --sqlite /absolute/path/to/your.db --table your_table_name`

## Unified Output
The cleaned merged output is generated at:
- `ml/data/processed/unified_endocrine_dataset.csv`

## Notes
- Do not commit private patient-identifiable data.
- Replace direct identifiers with hashed IDs before training.
- Keep `source` column to track origin of each row.
