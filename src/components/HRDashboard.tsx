import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { EmployeeCard } from "./EmployeeCard";
import { api } from "@/lib/api";
import { Loader2 } from "lucide-react";
import { toast } from "@/components/ui/use-toast";

interface HRDashboardProps {
  onLogout: () => void;
}

// Define types for API responses
interface EmployeeInsight {
  id: string;
  employee_id: string;
  name: string;
  team: string;
  department: string;
  last_check_in: string;
  status: "excellent" | "stable" | "improving" | "declining";
  mood_trend: string[];
  risk_level: string;
}

interface EmployeeTrend {
  period: string;
  total_sessions: number;
  mood_distribution: Record<string, number>;
  common_topics: string[];
}

interface EmployeeRisk {
  employee_id: string;
  name: string;
  team: string;
  department: string;
  last_check_in: string;
  risk_level: string;
  risk_factors: string[];
  recommended_actions: string[];
}

interface HRInsightsResponse {
  insights: EmployeeInsight[];
}

interface HRTrendsResponse {
  trends: EmployeeTrend[];
}

interface HRAtRiskResponse {
  at_risk_employees: EmployeeRisk[];
}

export const HRDashboard = ({ onLogout }: HRDashboardProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [employees, setEmployees] = useState<EmployeeInsight[]>([]);
  const [atRiskEmployees, setAtRiskEmployees] = useState<EmployeeRisk[]>([]);
  const [trends, setTrends] = useState<EmployeeTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [departments, setDepartments] = useState<string[]>([]);

  // Fetch data from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch insights
        const insightsResponse = await api.get<HRInsightsResponse>('/hr/insights');
        setEmployees(insightsResponse.data.insights);
        
        // Extract unique departments
        const uniqueDepartments = Array.from(
          new Set(insightsResponse.data.insights.map(e => e.department))
        ) as string[];
        setDepartments(uniqueDepartments);
        
        // Fetch at-risk employees
        const atRiskResponse = await api.get<HRAtRiskResponse>('/hr/at-risk');
        setAtRiskEmployees(atRiskResponse.data.at_risk_employees);
        
        // Fetch trends
        const trendsResponse = await api.get<HRTrendsResponse>('/hr/trends');
        setTrends(trendsResponse.data.trends);
      } catch (error) {
        console.error('Error fetching HR data:', error);
        toast({
          title: "Error fetching data",
          description: "Could not load HR dashboard data. Please try again later.",
          variant: "destructive"
        });
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  // Filter employees based on search and filters
  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.team.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDepartment = departmentFilter === "all" || employee.department === departmentFilter;
    const matchesStatus = statusFilter === "all" || employee.status === statusFilter;
    
    return matchesSearch && matchesDepartment && matchesStatus;
  });

  const getStatusStats = () => {
    const stats = {
      excellent: employees.filter(e => e.status === "excellent").length,
      stable: employees.filter(e => e.status === "stable").length,
      improving: employees.filter(e => e.status === "improving").length,
      declining: employees.filter(e => e.status === "declining").length,
    };
    return stats;
  };

  const stats = getStatusStats();

  return (
    <div className="min-h-screen bg-gradient-wellness">
      {/* Header */}
      <div className="bg-card/80 backdrop-blur-sm border-b border-border/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-light text-foreground">RUHANI Dashboard</h1>
              <p className="text-sm text-muted-foreground">Employee Wellness Overview</p>
            </div>
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                className="border-primary/30 hover:bg-primary/10"
              >
                Export Report
              </Button>
              <Button
                onClick={onLogout}
                variant="outline"
                className="border-destructive/30 hover:bg-destructive/10 text-destructive"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="p-4 bg-success/10 border-success/20">
            <div className="text-center">
              <div className="text-2xl font-semibold text-success">{stats.excellent}</div>
              <div className="text-sm text-success/80">Excellent</div>
            </div>
          </Card>
          <Card className="p-4 bg-primary/10 border-primary/20">
            <div className="text-center">
              <div className="text-2xl font-semibold text-primary">{stats.stable}</div>
              <div className="text-sm text-primary/80">Stable</div>
            </div>
          </Card>
          <Card className="p-4 bg-warning/10 border-warning/20">
            <div className="text-center">
              <div className="text-2xl font-semibold text-warning">{stats.improving}</div>
              <div className="text-sm text-warning/80">Improving</div>
            </div>
          </Card>
          <Card className="p-4 bg-destructive/10 border-destructive/20">
            <div className="text-center">
              <div className="text-2xl font-semibold text-destructive">{stats.declining}</div>
              <div className="text-sm text-destructive/80">Need Attention</div>
            </div>
          </Card>
        </div>

        {/* Filters */}
        <Card className="p-6 mb-6 bg-card/80 backdrop-blur-sm">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search employees or teams..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="h-10 rounded-lg border-primary/20 focus:border-primary/50"
              />
            </div>
            <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
              <SelectTrigger className="w-full md:w-48 h-10 rounded-lg border-primary/20">
                <SelectValue placeholder="Department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Departments</SelectItem>
                {departments.map(dept => (
                  <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-48 h-10 rounded-lg border-primary/20">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="excellent">Excellent</SelectItem>
                <SelectItem value="stable">Stable</SelectItem>
                <SelectItem value="improving">Improving</SelectItem>
                <SelectItem value="declining">Need Attention</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </Card>

        {/* Loading State */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Loading dashboard data...</p>
          </div>
        ) : (
          <>
            {/* Employee Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredEmployees.map((employee) => (
                <EmployeeCard 
                  key={employee.id} 
                  employee={{
                    id: parseInt(employee.employee_id),
                    name: employee.name,
                    avatar: "/api/placeholder/60/60",
                    department: employee.department,
                    team: employee.team,
                    lastCheckIn: employee.last_check_in || new Date().toISOString(),
                    moodTrend: employee.mood_trend.map(mood => {
                      // Convert mood strings to numbers for visualization
                      if (mood === "happy") return 5;
                      if (mood === "neutral") return 3;
                      if (mood === "stressed") return 2;
                      if (mood === "anxious") return 2;
                      if (mood === "overwhelmed") return 1;
                      return 3; // Default
                    }),
                    status: employee.status,
                    insights: `Risk level: ${employee.risk_level}. Recent mood trends show ${employee.status} patterns.`
                  }} 
                />
              ))}
            </div>

            {filteredEmployees.length === 0 && !loading && (
              <div className="text-center py-12">
                <p className="text-muted-foreground">No employees match your current filters.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};