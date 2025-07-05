import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { EmployeeCard } from "./EmployeeCard";

interface HRDashboardProps {
  onLogout: () => void;
}

// Mock employee data
const mockEmployees = [
  {
    id: 1,
    name: "Alex Johnson",
    avatar: "/api/placeholder/60/60",
    department: "Engineering",
    team: "Frontend",
    lastCheckIn: "2024-01-15",
    moodTrend: [3, 4, 2, 4, 3],
    status: "stable" as const,
    insights: "Generally positive with occasional stress during sprint deadlines."
  },
  {
    id: 2,
    name: "Sarah Chen",
    avatar: "/api/placeholder/60/60",
    department: "Design",
    team: "UX",
    lastCheckIn: "2024-01-14",
    moodTrend: [2, 2, 3, 3, 4],
    status: "improving" as const,
    insights: "Showing steady improvement after team restructuring."
  },
  {
    id: 3,
    name: "Marcus Williams",
    avatar: "/api/placeholder/60/60",
    department: "Engineering",
    team: "Backend",
    lastCheckIn: "2024-01-13",
    moodTrend: [4, 3, 2, 2, 1],
    status: "declining" as const,
    insights: "Noticeable decline in mood. Recommend wellness check-in."
  },
  {
    id: 4,
    name: "Emma Davis",
    avatar: "/api/placeholder/60/60",
    department: "Marketing",
    team: "Content",
    lastCheckIn: "2024-01-15",
    moodTrend: [4, 4, 5, 4, 5],
    status: "excellent" as const,
    insights: "Consistently high mood and engagement levels."
  }
];

export const HRDashboard = ({ onLogout }: HRDashboardProps) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  // Filter employees based on search and filters
  const filteredEmployees = mockEmployees.filter(employee => {
    const matchesSearch = employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.team.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDepartment = departmentFilter === "all" || employee.department === departmentFilter;
    const matchesStatus = statusFilter === "all" || employee.status === statusFilter;
    
    return matchesSearch && matchesDepartment && matchesStatus;
  });

  const getStatusStats = () => {
    const stats = {
      excellent: mockEmployees.filter(e => e.status === "excellent").length,
      stable: mockEmployees.filter(e => e.status === "stable").length,
      improving: mockEmployees.filter(e => e.status === "improving").length,
      declining: mockEmployees.filter(e => e.status === "declining").length,
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
                <SelectItem value="Engineering">Engineering</SelectItem>
                <SelectItem value="Design">Design</SelectItem>
                <SelectItem value="Marketing">Marketing</SelectItem>
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
            <p className="text-muted-foreground">No employees match your current filters.</p>
          </div>
        )}
      </div>
    </div>
  );
};