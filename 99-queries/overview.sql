SELECT
    datestamp::date AS datestamp,
    CASE
        WHEN score < slo_min THEN score
        ELSE null
    END AS red,
    CASE
        WHEN score >= slo_min AND score < slo THEN score
        ELSE null
    END AS amber,
    CASE
        WHEN score >= slo THEN score
        ELSE null
    END AS green
FROM
    (
        SELECT
            datestamp,
            sum(weighted_score) / sum(weight) AS score,
            avg(slo) AS slo,
            avg(slo_min) AS slo_min
        FROM
            (
                SELECT
                    metric_id,
                    weight,
                    datestamp,
                    sum(totalok) / sum(total) * weight AS weighted_score,
                    avg(slo_min) AS slo_min,
                    avg(slo) AS slo
                FROM v_summary
                WHERE
                    (
                        '${category:Singlequote}' = 'All'
                        OR '${category:Singlequote}' = category
                    )
                    AND (
                        '${metric:Singlequote}' = 'All'
                        OR '${metric:Singlequote}' = metric_id
                    )
                    AND (
                        '${business_unit:Singlequote}' = 'All'
                        OR '${business_unit:Singlequote}' = business_unit
                    )
                GROUP BY
                    metric_id, datestamp, weight
            ) AS q1
        GROUP BY datestamp
    ) AS q2
ORDER BY datestamp ASC
