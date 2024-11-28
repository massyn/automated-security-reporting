# Data Model

## Collectors

The collectors will save the result from the APIs in their native `json` format.  A number of additional field are appended to the data source.

```mermaid
erDiagram
    collectors {
        string _tenancy             "The result of the TENANT variable (if it is set)"
        string _upload_timestamp    "Timestamp of when the download occurred."
        string _upload_id           "Unique ID that is set to all downloads that occurred by this collector."
    }
```

## Metrics

### Metric definition

TODO

### Metric

```mermaid
erDiagram
    metric {
        string resource      "The unique identifer of the resource being measured."
        string resource_type "The type of resource being measured, used for attribution."
        float  compliance    "The compliance state of the resource, represented as a percentage (float value between 0 and 1)"
        string detail         "Additional information to aid with remediation."
    }
```