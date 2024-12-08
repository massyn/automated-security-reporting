# automated-security-reporting

[![Build](https://github.com/massyn/automated-security-reporting/actions/workflows/build.yml/badge.svg)](https://github.com/massyn/automated-security-reporting/actions/workflows/build.yml) ![Docker Pulls](https://img.shields.io/docker/pulls/massyn/asr)

Automated Security Reporting is a continuous assurance or executive cyber security reporting solution.  A number of [collectors](00-docs/collectors.md) and [metrics](00-docs/metrics.md) are currently supported, with more coming.

> Got an idea for a new collector or a metric?  Submit yours now as an [issue](https://github.com/massyn/automated-security-reporting/issues/new).

![overview](00-docs/overview.png)

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
    metrics.data -- backup --> s3
    
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

    dashboard.web -- upload --> s3web[(AWS S3)]:::data

    classDef source stroke:#0f0
    classDef data stroke:#00f
    classDef code stroke:#f00
    classDef config stroke:#ff0

    classDef dim fill:#f9c6c9,stroke:#000,stroke-width:2px,color:#000;
    classDef calc fill:#c6d8f9,stroke:#000,stroke-width:2px,color:#000;
```

### Information flow

```mermaid
graph LR
    source:::source
    environment[environment variables]:::config
    s3[(AWS S3)]:::data

    subgraph collector
        
        collector.wrapper[wrapper]:::code
        collector.src[src_*]:::code
        collector.json[(*.json)]:::data

        collector.src --> collector.json
    end
    source --> collector.src
    environment --> collector.wrapper
    collector.wrapper --> collector.src
    collector.json -- backup --> s3

    subgraph metrics
        metrics.metrics[metrics]:::code
        metrics.yaml[yaml]:::config
        metrics.df[metrics.parquet]:::data
    end
    collector.json --> metrics.metrics
    metrics.yaml --> metrics.metrics
    metrics.metrics --> metrics.df

    subgraph pipeline
        pipeline.pipeline[pipeline]:::code

        pipeline.data[(data)]:::data

        pipeline.prepdashboard[Prepare Dashboard]:::code

        pipeline.pipeline --> pipeline.data
    end
    metrics.df --> pipeline.pipeline
    
    pipeline.data --> pipeline.prepdashboard
    pipeline.data -- backup --> s3
    
    port
    subgraph dashboard
        dashboard.data[(data)]:::data
        dashboard.web[web]
        dashboard.server[web server]:::code
    end
    dashboard.web --> dashboard.server
    dashboard.server --> port
    pipeline.prepdashboard --> dashboard.data
    dashboard.data --> dashboard.web

    pipeline.prepdashboard -- upload --> s3web[(AWS S3)]:::data

    classDef source stroke:#0f0
    classDef data stroke:#00f
    classDef code stroke:#f00
    classDef config stroke:#ff0

    classDef dim fill:#f9c6c9,stroke:#000,stroke-width:2px,color:#000;
    classDef calc fill:#c6d8f9,stroke:#000,stroke-width:2px,color:#000;
```

## Quick start using Docker

Grab your Crowdstrike API keys. (or if not Crowdstrike, any of the built-in [collectors](00-docs/collectors.md)).

Run

```bash
docker run -p 80:80 \
    -e FALCON_CLIENT_ID="xxx" \
    -e FALCON_SECRET="xxx" \
    -t massyn/asr:main 
```

Open your browser to http://localhost, and view your dashboard.

### Modes of operation

By default, the Docker instance will start up, do an extraction, and update the local website on the running instance.

The instance can also run in an extract-only mode, where the data will be downloaded and processed, and optionally also updated to a target S3 hosted website.

A typical use case would entail the following :

```bash
docker run -p 80:80 \
    -e FALCON_CLIENT_ID="xxx" \
    -e FALCON_SECRET="xxx" \
    -e STORE_AWS_S3_BUCKET=my-s3-bucket-name \
    -e STORE_AWS_S3_WEB=my-s3-bucket-name-web \
    -e EXTRACT_ONLY=true \
    -td massyn/asr:main 
```

where

* `STORE_AWS_S3_BUCKET` is the AWS S3 bucket where the target data files will be stored to retain state.
* `STORE_AWS_S3_WEB` is the AWS S3 bucket where the static website is served from.
* `EXTRACT_ONLY` will only do the extract, update the target S3 website, and then terminate.

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

* Setting up the [Dashboard](00-docs/dashboard.md)