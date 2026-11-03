# Data

The original dataset is in `data/raw/hillstrom.csv`, unmodified. To validate it (or download it if it is missing):

```bash
python src/download_data.py
```

The script checks that it has the expected 12 columns and 64,000 rows.

If you need to download it again and the link fails, get the file manually from the [MineThatData blog](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html) or from Kaggle (search for "Hillstrom email marketing") and save it under that name.

## Source

Kevin Hillstrom, *MineThatData E-Mail Analytics and Data Mining Challenge* (2008).

| | |
|---|---|
| Customers | 64,000 who bought in the past 12 months |
| Groups | Men's email, women's email, no email (random assignment) |
| Outcome window | 2 weeks after the send |
| Columns | 12 (see the data dictionary in `notebooks/01_validation.ipynb`) |
| Size | ~3.8 MB |
