CREATE TABLE IF NOT EXISTS summary
(
    total double precision,
    totalok double precision,
    metric_id text,
    title text,
    slo double precision,
    slo_min double precision,
    weight double precision,
    category text,
    datestamp text,
    business_unit text,
    team text,
    location text
);

DELETE FROM summary
WHERE (metric_id, datestamp) IN (
    SELECT DISTINCT
        d.metric_id,
        d.datestamp
    FROM
        detail d
);

INSERT INTO summary (
    metric_id,
    title,
    datestamp,
    slo,
    slo_min,
    weight,
    category,
    business_unit,
    team,
    location,
    total,
    totalok
)
SELECT
    d.metric_id,
    d.title,
    d.datestamp,
    d.slo,
    d.slo_min,
    d.weight,
    d.category,
    d.business_unit,
    d.team,
    d.location,
    COUNT(d.compliance) AS total,
    SUM(d.compliance) AS totalok
FROM
    detail d
GROUP BY
    d.metric_id,
    d.title,
    d.datestamp,
    d.slo,
    d.slo_min,
    d.weight,
    d.category,
    d.business_unit,
    d.team,
    d.location;