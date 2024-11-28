# How to run metrics

## Quick start

```bash
cd 02-metrics
python metrics.py
```

## Command line options

### Command-Line Parameters

| Option             | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `-h`               | Display the help file.                                                     |
| `-dryrun`          | Run all metrics in test mode without updating the target repository.       |
| `-metric <metric id>` | Run a specific metric in test mode, using the specified metric ID.        |
| `-path`            | Specify the path to the metric YAML files. Defaults to the current path.   |
| `-data`            | Specify the path to the data source. Defaults to `../data/source`.         |
| `-parquet`         | Specify the path where the parquet files will be stored. Defaults to `../data`. |
