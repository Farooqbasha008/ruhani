import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import employeeAvatar from "@/assets/employee-avatar.jpg";

interface Employee {
  id: number;
  name: string;
  avatar: string;
  department: string;
  team: string;
  lastCheckIn: string;
  moodTrend: number[];
  status: "excellent" | "stable" | "improving" | "declining";
  insights: string;
}

interface EmployeeCardProps {
  employee: Employee;
}

export const EmployeeCard = ({ employee }: EmployeeCardProps) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "excellent":
        return "bg-success/20 text-success border-success/30";
      case "stable":
        return "bg-primary/20 text-primary border-primary/30";
      case "improving":
        return "bg-warning/20 text-warning border-warning/30";
      case "declining":
        return "bg-destructive/20 text-destructive border-destructive/30";
      default:
        return "bg-muted/20 text-muted-foreground border-muted/30";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "excellent":
        return "Excellent";
      case "stable":
        return "Stable";
      case "improving":
        return "Improving";
      case "declining":
        return "Needs Attention";
      default:
        return "Unknown";
    }
  };

  // Simple mood trend visualization
  const renderMoodTrend = () => {
    return (
      <div className="flex items-end space-x-1 h-8">
        {employee.moodTrend.map((mood, index) => (
          <div
            key={index}
            className="bg-primary/60 rounded-sm transition-smooth hover:bg-primary"
            style={{
              width: "8px",
              height: `${mood * 6}px`,
              minHeight: "4px"
            }}
          />
        ))}
      </div>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Card className="p-6 bg-card/80 backdrop-blur-sm shadow-card border-0 hover:shadow-glow transition-smooth">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <img
            src={employeeAvatar}
            alt={employee.name}
            className="w-12 h-12 rounded-full shadow-soft"
          />
          <div>
            <h3 className="font-medium text-foreground">{employee.name}</h3>
            <p className="text-sm text-muted-foreground">
              {employee.team} • {employee.department}
            </p>
          </div>
        </div>
        <Badge className={`${getStatusColor(employee.status)} text-xs px-2 py-1`}>
          {getStatusText(employee.status)}
        </Badge>
      </div>

      {/* Mood Trend */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-foreground">Mood Trend</span>
          <span className="text-xs text-muted-foreground">
            Last 5 sessions
          </span>
        </div>
        {renderMoodTrend()}
      </div>

      {/* Insights */}
      <div className="mb-4">
        <p className="text-sm text-muted-foreground line-clamp-2">
          {employee.insights}
        </p>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-border/50">
        <span className="text-xs text-muted-foreground">
          Last check-in: {formatDate(employee.lastCheckIn)}
        </span>
        <Button
          size="sm"
          variant="outline"
          className="h-8 px-3 text-xs border-primary/30 hover:bg-primary/10 
                     hover:border-primary/50 transition-smooth rounded-lg"
        >
          View Report
        </Button>
      </div>
    </Card>
  );
};