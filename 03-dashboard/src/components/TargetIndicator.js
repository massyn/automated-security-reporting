import React from 'react';
import { LinearProgress, Typography } from "@mui/material";

export const determineComplianceColor = ( currentPercentage,slo,sloMin) => {
    if (currentPercentage >= slo) {
      return "success";
    } else if (currentPercentage >= sloMin) {
      return "warning";
    } else {
      return "error";
    }
};

const TargetIndicator = ({ metric } ) => {
    return (
        <div style={{ display: "flex", flexDirection: "column", gap: 0.5 }}>
        <div style={{ width: "150px", height: "12px" }}>
            <LinearProgress
            variant="determinate"
            value={metric.score * 100}
            style={{ height: "12px", borderRadius: 5 }}
            color={determineComplianceColor(
                metric.score,
                metric.slo,
                metric.slo_min
            )}
            />
            <div
            style={{
                position: "relative",
                left: `${metric.slo * 100}%`,
                top: "-15px",
                height: "18px",
                width: "1px",
                background: "#616161",
            }}
            ></div>
        </div>
        <Typography color="textPrimary" variant="subtitle2" fontWeight={500}>
            Target: {Math.round(metric.slo * 100)}%
        </Typography>
        </div>
  );
}

export default TargetIndicator;