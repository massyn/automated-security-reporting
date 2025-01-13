SELECT
    category,
    CASE
        WHEN score < slo_min THEN score
    END AS red,
    CASE
        WHEN score >= slo_min AND score < slo THEN score
    END AS amber,
    CASE
        WHEN score >= slo THEN score
    END AS green
FROM
    (
        SELECT
            category,
            sum(weighted_score) / sum(weight) AS score,
            avg(slo) AS slo,
            avg(slo_min) AS slo_min
        FROM
            (
                SELECT
                    metric_id,
                    weight,
                    category,
                    sum(totalok) / sum(total) * weight AS weighted_score,
                    avg(slo_min) AS slo_min,
                    avg(slo) AS slo
                FROM v_summary
                WHERE
                    datestamp = (
                        SELECT max(datestamp)
                        FROM
                            v_summary
                    )
                    AND (
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
                    metric_id, category, weight
            ) AS q1
        GROUP BY category
    ) AS q2
ORDER BY score ASC
