# Integration Tests

Integration tests verify that Aladdin Analyst AI components work together correctly through the public API.

## Current Coverage

### End-to-End Analysis Workflow

The `test_end_to_end.py` test validates the complete CSV analysis workflow:

1. Load a CSV dataset.
2. Generate an initial data profile.
3. Assess initial data quality.
4. Apply configured missing-value strategies.
5. Remove duplicate rows.
6. Remove constant columns.
7. Generate the final data profile.
8. Verify the final data quality report.

## Test Dataset

The workflow uses `datasets/sample/messy_sales.csv`, which contains:

- Missing values across multiple columns.
- A duplicated record.
- A constant column.
- Both numerical and categorical data.

## Running Integration Tests

Run only integration tests:

```powershell
python -m pytest tests/integration -v
```

Run the complete test suite:

```powershell
python -m pytest -v
```

## Expected Outcome

The end-to-end workflow should:

- Reduce the dataset from 8 rows to 7.
- Reduce the number of columns from 7 to 6.
- Fill 4 missing values.
- Remove 1 duplicate row.
- Remove 1 constant column.
- Produce a final dataset with no missing values.
- Pass the implemented data quality checks.

Integration tests complement unit tests; they do not replace them.