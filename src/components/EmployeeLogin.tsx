import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { useEmployeeApi } from "@/hooks/useEmployeeApi";
import ruhaniLogo from "@/assets/ruhani-logo.png";

interface EmployeeLoginProps {
  onLoginSuccess: (employeeId: string, employeeName: string) => void;
  onShowOnboarding: () => void;
  onBackToHome?: () => void;
}

export const EmployeeLogin = ({ onLoginSuccess, onShowOnboarding, onBackToHome }: EmployeeLoginProps) => {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");

  const { toast } = useToast();
  const { loginEmployee } = useEmployeeApi();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      setError("Please enter your email address.");
      return;
    }

    try {
      const result = await loginEmployee.mutateAsync({ email });
      
      if (result.success) {
        toast({
          title: "Welcome back!",
          description: `Good to see you again, ${result.name}!`,
        });
        
        onLoginSuccess(result.employee_id, result.name);
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Login failed. Please try again.";
      setError(errorMessage);
      
      toast({
        title: "Login Failed",
        description: errorMessage,
        variant: "destructive"
      });
    }
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
          <h1 className="text-2xl font-light text-foreground/90">Welcome Back</h1>
          <p className="text-sm text-muted-foreground">Sign in to continue your wellness journey</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.email@company.com"
              className="mt-1"
              required
            />
          </div>

          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            className="w-full h-12 text-lg font-medium bg-primary hover:bg-primary/90 
                     shadow-soft transition-smooth rounded-xl"
            disabled={loginEmployee.isPending}
          >
            {loginEmployee.isPending ? "Signing In..." : "Sign In"}
          </Button>

          <div className="space-y-3">
            <div className="text-center">
              <p className="text-sm text-muted-foreground">
                New to RUHANI?{" "}
                <button
                  type="button"
                  onClick={onShowOnboarding}
                  className="text-primary hover:text-primary/80 underline"
                >
                  Create an account
                </button>
              </p>
            </div>

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
        </form>

        <p className="text-xs text-muted-foreground text-center mt-4">
          Your wellness data is secure and private
        </p>
      </Card>
    </div>
  );
}; 