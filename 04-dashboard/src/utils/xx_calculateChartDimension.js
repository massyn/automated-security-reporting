import { filterData, pivotData } from './processData';

export const calculateChartDimension = (data, filters = {}, z) => {
    const filteredData = filterData(data,filters);  // Apply filters
  
    // pivot the first layer
    const chart2_pivotData = pivotData(filteredData, ['datestamp', 'metric_id', z], {
      sum_total:   [ 'sum', 'total'   ],
      sum_totalok: [ 'sum', 'totalok' ],
      weight:      [ 'avg', 'weight'  ],
      slo:         [ 'avg', 'slo'     ],
      slo_min:     [ 'avg', 'slo_min' ]
    });
    
    const chart2_weights = pivotData(chart2_pivotData, ['datestamp',z], {
      sum_weight: ['sum', 'weight'],
    });
    
    const chart2_weightsLookup = chart2_weights.reduce((lookup, item) => {
      if (!lookup[item.datestamp]) {
        lookup[item.datestamp] = {};
      }
      lookup[item.datestamp][item[z]] = item.sum_weight;
      return lookup;
    }, {});
    
    const chart2_pivotData_calculated = chart2_pivotData.map((item) => ({
      ...item,
      score_weighted:   item.sum_total ? (item.sum_totalok / item.sum_total) * item.weight : 0,
      slo_weighted:     item.slo * item.weight,
      slo_min_weighted: item.slo_min * item.weight,
      weighted_sum:     chart2_weightsLookup[item.datestamp]?.[item[z]] || 0,
      z:                item[z],
    }));
    
    const chart2_pivotData_calculated2 = pivotData(chart2_pivotData_calculated, ['datestamp', z], {
      score_weighted_total: [ 'sum', 'score_weighted'   ],
      weighted_sum_total:   [ 'sum', 'weighted_sum'     ],
      weighted_slo:         [ 'sum', 'slo_weighted'     ],
      weighted_slo_min:     [ 'sum', 'slo_min_weighted' ]
    });

    const chart2_pivotData_calculated3 = chart2_pivotData_calculated2.map((item) => {
      const weightSum = item.weighted_sum_total || 0;
      return {
        ...item,
        z: item[z],
        value: weightSum ? item.score_weighted_total / weightSum : 0,
        slo: weightSum ? item.weighted_slo / weightSum : 0,
        slo_min: weightSum ? item.weighted_slo_min / weightSum : 0,
      };
    });
    
    return chart2_pivotData_calculated3
  };