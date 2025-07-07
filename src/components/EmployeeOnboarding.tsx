import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { useEmployeeApi } from "@/hooks/useEmployeeApi";
import ruhaniLogo from "@/assets/ruhani-logo.png";

interface EmployeeOnboardingProps {
  onOnboardingComplete: (employeeId: string) => void;
  onBackToLogin?: () => void;
  onBackToHome?: () => void;
}

export const EmployeeOnboarding = ({ onOnboardingComplete, onBackToLogin, onBackToHome }: EmployeeOnboardingProps) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    department: "",
    role: "",
    github: "",
    linkedin: "",
    cultural_background: "",
    preferred_language: "en"
  });

  const { toast } = useToast();
  const { onboardEmployee } = useEmployeeApi();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.department || !formData.role) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields.",
        variant: "destructive"
      });
      return;
    }

    try {
      const result = await onboardEmployee.mutateAsync(formData);
      
      if (result.success) {
        toast({
          title: "Welcome to RUHANI!",
          description: "Your account has been created successfully.",
        });
        
        // Store employee name in localStorage
        localStorage.setItem('employee_name', formData.name);
        
        onOnboardingComplete(result.employee_id);
      }
    } catch (error) {
      toast({
        title: "Onboarding Failed",
        description: "Please try again or contact support.",
        variant: "destructive"
      });
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-gradient-wellness flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 shadow-card border-0 bg-card/80 backdrop-blur-sm">
        {/* Logo */}
        <div className="mb-8 text-center">
          <img 
            src={ruhaniLogo} 
            alt="RUHANI" 
            className="w-24 h-24 mx-auto mb-4"
          />
          <h1 className="text-2xl font-light text-foreground/90">Welcome to RUHANI</h1>
          <p className="text-sm text-muted-foreground">Let's get you set up</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Required Fields */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Full Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                placeholder="Enter your full name"
                className="mt-1"
                required
              />
            </div>

            <div>
              <Label htmlFor="email">Email Address *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                placeholder="your.email@company.com"
                className="mt-1"
                required
              />
            </div>

            <div>
              <Label htmlFor="department">Department *</Label>
              <Select value={formData.department} onValueChange={(value) => handleInputChange("department", value)}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select your department" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Engineering">Engineering</SelectItem>
                  <SelectItem value="Design">Design</SelectItem>
                  <SelectItem value="Marketing">Marketing</SelectItem>
                  <SelectItem value="Sales">Sales</SelectItem>
                  <SelectItem value="HR">Human Resources</SelectItem>
                  <SelectItem value="Finance">Finance</SelectItem>
                  <SelectItem value="Operations">Operations</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="role">Job Role *</Label>
              <Input
                id="role"
                value={formData.role}
                onChange={(e) => handleInputChange("role", e.target.value)}
                placeholder="e.g., Software Engineer, Designer"
                className="mt-1"
                required
              />
            </div>
          </div>

          {/* Optional Fields */}
          <div className="space-y-4">
            <div>
              <Label htmlFor="github">GitHub Profile (Optional)</Label>
              <Input
                id="github"
                value={formData.github}
                onChange={(e) => handleInputChange("github", e.target.value)}
                placeholder="https://github.com/username"
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="linkedin">LinkedIn Profile (Optional)</Label>
              <Input
                id="linkedin"
                value={formData.linkedin}
                onChange={(e) => handleInputChange("linkedin", e.target.value)}
                placeholder="https://linkedin.com/in/username"
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="cultural_background">Cultural Background (Optional)</Label>
              <Input
                id="cultural_background"
                value={formData.cultural_background}
                onChange={(e) => handleInputChange("cultural_background", e.target.value)}
                placeholder="e.g., South Asian, Latin American, European"
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="preferred_language">Preferred Language</Label>
              <Select value={formData.preferred_language} onValueChange={(value) => handleInputChange("preferred_language", value)}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Spanish</SelectItem>
                  <SelectItem value="fr">French</SelectItem>
                  <SelectItem value="de">German</SelectItem>
                  <SelectItem value="zh">Chinese</SelectItem>
                  <SelectItem value="ja">Japanese</SelectItem>
                  <SelectItem value="ko">Korean</SelectItem>
                  <SelectItem value="hi">Hindi</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            className="w-full h-12 text-lg font-medium bg-primary hover:bg-primary/90 
                     shadow-soft transition-smooth rounded-xl"
            disabled={onboardEmployee.isPending}
          >
            {onboardEmployee.isPending ? "Creating Account..." : "Create Account"}
          </Button>

          <div className="space-y-2 mt-4">
            {onBackToLogin && (
              <div className="text-center">
                <button
                  type="button"
                  onClick={onBackToLogin}
                  className="text-sm text-primary hover:text-primary/80 underline"
                >
                  ← Back to Login
                </button>
              </div>
            )}

            {onBackToHome && (
              <div className="text-center">
                <button
                  type="button"
                  onClick={onBackToHome}
                  className="text-sm text-muted-foreground hover:text-foreground underline"
                >
                  ← Back to Home
                </button>
              </div>
            )}
          </div>

          <p className="text-xs text-muted-foreground text-center">
            Your information is secure and will only be used to provide personalized wellness support.
          </p>
        </form>
      </Card>
    </div>
  );
}; 