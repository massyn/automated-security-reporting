# automated-security-reporting
Open Source Security Report Platform

## High Level Architecture

```mermaid
graph LR
    source:::source
    environment[environment variables]:::config
    s3[(AWS S3)]:::data

    subgraph collector
        
        collector.extract[extract]:::code
        collector.data[(data)]:::data

        collector.extract --> collector.data
    end
    source --> collector.extract
    environment --> collector.extract
    collector.data -- backup --> s3

    subgraph pipeline
        metrics.definition[metric definitions]:::config
        metrics.process[metrics]:::code
        metrics.pipeline[pipeline]:::code

        metrics.data[(data)]:::data

        metrics.process --> metrics.pipeline
        metrics.pipeline --> metrics.data

        metrics.prepdashboard[Prepare Dashboard]:::code
    end
    metrics.definition --> metrics.process
    collector.data --> metrics.process
    metrics.data --> metrics.prepdashboard
    
    port
    subgraph dashboard
        dashboard.data[(data)]:::data
        dashboard.web[web]
        dashboard.server[web server]:::code
    end
    dashboard.web --> dashboard.server
    dashboard.server --> port
    metrics.prepdashboard --> dashboard.data
    dashboard.data --> dashboard.web

    classDef source stroke:#0f0
    classDef data stroke:#00f
    classDef code stroke:#f00
    classDef config stroke:#ff0

    classDef dim fill:#f9c6c9,stroke:#000,stroke-width:2px,color:#000;
    classDef calc fill:#c6d8f9,stroke:#000,stroke-width:2px,color:#000;
```

## Architecture

* [Data Model](00-docs/data-model.md)
* [Data Flow](00-docs/data-flow.md)

## Collectors

* [How to](00-docs/how-to-run-an-extraction.md) run an extraction
* [Writing](00-docs/writing-a-collector.md) your own collector
* [List](00-docs/collectors.md) of collectors that can be used

## Metrics

* [How to](00-docs/how-to-run-metrics.md) run metrics
* [Creating](00-docs/create-a-metric.md) a metric
* [List](00-docs/metrics.md) of metrics

## Dashboard

TODO