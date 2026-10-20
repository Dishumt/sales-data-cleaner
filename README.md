# Sales Data Cleaning Tool
#### Video Demo:  <https://youtu.be/0TMrzF6PtXE>
#### Description:
Sales Data Cleaning Tool is a small CLI script I built to clean up mess in raw sales CSV files (Required columns: "Invoice", "StockCode", "Price", "Quantity"). It automatically checks every record and splits the input into two files: cleaned.csv for valid data and removed.csv for everything that got filtered out.

Basically, it drops rows with missing essential fields (IDs, price, quantity), invalid numeric values (like negative prices or non-numeric entries), and duplicate records. Moving the bad rows into a separate file,     indicating removal reasons for each, which makes it easy to audit what was removed without losing any data.

### Design Choices
* **Audit Logging with Boolean Masking in `clean_data()`** Implemented boolean masks (`bad_mask`) using indexer `.loc[]` to track why each row was filtered out. This allowed efficient logging of removal reasons into `removed.csv` without compromising execution performance on large datasets.
* **Removal Reason Analysis in `report()`:** Chose Pandas native `.explode()` over a manual Python loop for multi-label reason parsing to increase execution speed and maintain a clean, vectorized processing chain.
* **test script** Utilized small, synthetic DataFrames, `monkeypatch`, and Pytest's `tmp_path`. This isolates tests from external I/O dependencies, like `Year_2009-2010.csv`, ensuring expected behavior and fast test execution.

### Project Structure
* `project.py`: Core application logic containing data cleaning, SQLite export, and CLI interface.
* `test_project.py`: Unit tests using `pytest` to verify core cleaning logic.
* `requirements.txt`: Required dependencies.

## Dataset Options

* **Quick Test:** Use the included `sample_data.csv` for an immediate run:
  ```bash
  python project.py sample_data.csv
  
* **Full Dataset:** Unzip Year 2009-2010.zip to get the full CSV dataset (500k+ records) and run:
  ```bash
  python project.py "Year 2009-2010.csv"


