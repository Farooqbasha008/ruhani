import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ruhaniLogo from "@/assets/ruhani-logo.png";

interface HRLoginProps {
  onLogin: () => void;
}

export const HRLogin = ({ onLogin }: HRLoginProps) => {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Demo password - in real app this would be proper authentication
    if (password === "hr2024") {
      setError("");
      onLogin();
    } else {
      setError("Invalid password. Try 'hr2024' for demo.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-wellness flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 shadow-card border-0 bg-card/90 backdrop-blur-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <img 
            src={ruhaniLogo} 
            alt="RUHANI" 
            className="w-20 h-20 mx-auto mb-4"
          />
          <h1 className="text-2xl font-light text-foreground mb-2">RUHANI</h1>
          <p className="text-sm text-muted-foreground">HR Dashboard Access</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="password" className="text-sm font-medium text-foreground">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter HR dashboard password"
              className="h-11 rounded-xl border-primary/20 focus:border-primary/50 
                         focus:ring-primary/20 transition-smooth"
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
            className="w-full h-11 font-medium bg-primary hover:bg-primary/90 
                       shadow-soft transition-smooth rounded-xl"
          >
            Access Dashboard
          </Button>
        </form>

        {/* Demo Info */}
        <div className="mt-6 p-4 bg-muted/50 rounded-lg">
          <p className="text-xs text-muted-foreground text-center">
            <strong>Demo:</strong> Use password "hr2024" to access the dashboard
          </p>
        </div>

        {/* Security Notice */}
        <p className="text-xs text-muted-foreground text-center mt-4">
          🔒 All employee data is encrypted and HIPAA compliant
        </p>
      </Card>
    </div>
  );
};