import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { EmployeeCard } from "./EmployeeCard";
import { useHrApi } from "@/hooks/useHrApi";

interface HRDashboardProps {
  onLogout: () => void;
}

export const HRDashboard = ({ onLogout }: HRDashboardProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  // Fetch real employee data from API
  const { getAllEmployees, getInsights } = useHrApi();
  const { data: employeesData, isLoading, error } = getAllEmployees;
  const { data: insightsData } = getInsights;

  // Transform API data to match EmployeeCard interface
  const employees = employeesData?.employees?.map((emp: any) => ({
    id: emp.employee_id,
    name: emp.name,
    avatar: "/api/placeholder/60/60", // Keep placeholder for now
    department: emp.department,
    team: emp.role,
    lastCheckIn: emp.last_session ? new Date(emp.last_session).toISOString().split('T')[0] : "Never",
    moodTrend: [emp.average_mood], // Simplified - could be enhanced with historical data
    status: emp.wellness_status as "excellent" | "stable" | "improving" | "declining",
    insights: emp.recommendations?.join(", ") || "No specific insights available."
  })) || [];

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

  // Get unique departments from real data
  const departments = [...new Set(employees.map(emp => emp.department))].filter(Boolean);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-wellness flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading employee data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-wellness flex items-center justify-center">
        <div className="text-center">
          <p className="text-destructive mb-4">Error loading employee data</p>
          <Button onClick={() => window.location.reload()} variant="outline">
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-wellness">
      {/* Header */}
      <div className="bg-card/80 backdrop-blur-sm border-b border-border/50 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-light text-foreground">RUHANI Dashboard</h1>
              <p className="text-sm text-muted-foreground">
                Employee Wellness Overview • {employees.length} Employees
              </p>
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

        {/* Employee Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEmployees.map((employee) => (
            <EmployeeCard key={employee.id} employee={employee} />
          ))}
        </div>

        {filteredEmployees.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">
              {employees.length === 0 
                ? "No employees found in the system." 
                : "No employees match your current filters."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};