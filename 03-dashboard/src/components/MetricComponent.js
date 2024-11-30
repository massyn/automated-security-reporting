import {
    // Button,
    Card,
    Link,
    Tooltip,
    Typography,
    useTheme,
  } from "@mui/material";
import TargetIndicator from "./TargetIndicator";
// import { NavigateNext } from "@mui/icons-material";
// import { useNavigate } from "react-router-dom";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";

const MetricComponent = ({ metric } ) => {
    // const navigate = useNavigate();
    const theme = useTheme();
    return (
      <Card
        variant="outlined"
        sx={{
          padding: 2,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 1,
          marginBottom: "0.5em",
        }}
        data-testid="metric"
      >
        <div>
          <Typography variant="subtitle1" fontWeight={400}>
            {metric.title}
            {metric.helptext && (
              <Tooltip title={metric.helptext} arrow placement="top">
                <Link href={metric.url} target="_blank" rel="noopener">
                  <HelpOutlineIcon
                    sx={{
                      color: theme.palette.primary.main,
                      verticalAlign: "sub",
                      fontSize: "1.25em",
                    }}
                  />
                </Link>
              </Tooltip>
            )}
          </Typography>
        </div>
        <div style={{ display: "flex", gap: "2em", alignItems: "center" }}>
          <TargetIndicator
            metric={metric}
          />
  
          <Typography variant="h4" sx={{ width: "75px" }}>
            {Math.round(metric.score * 100)}%
          </Typography>
  
          {/* <Button
            variant="contained"
            color="primary"
            size="medium"
            endIcon={<NavigateNext />}
            onClick={() => navigate(`/metric-details/${metric.metric_id}`)}
            disableElevation
          >
            View
          </Button> */}
        </div>
      </Card>
    );
}

export default MetricComponent;