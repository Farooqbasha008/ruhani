import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import employeeAvatar from "@/assets/employee-avatar.jpg";
import ruhaniLogo from "@/assets/ruhani-logo.png";

interface EmployeeWelcomeProps {
  userName?: string;
  onStartSession: () => void;
  onLogout: () => void;
  onBackToLogin?: () => void;
}

export const EmployeeWelcome = ({ 
  userName = "Alex", 
  onStartSession,
  onLogout,
  onBackToLogin
}: EmployeeWelcomeProps) => {
  return (
    <div className="min-h-screen bg-gradient-wellness flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 text-center shadow-card border-0 bg-card/80 backdrop-blur-sm">
        {/* Logo */}
        <div className="mb-8">
          <img 
            src={ruhaniLogo} 
            alt="RUHANI" 
            className="w-24 h-24 mx-auto mb-4"
          />
          <h1 className="text-2xl font-light text-foreground/90">RUHANI</h1>
          <p className="text-sm text-muted-foreground">Your invisible wellness companion</p>
        </div>

        {/* User Profile */}
        <div className="mb-8">
          <div className="relative mb-4">
            <img
              src={employeeAvatar}
              alt={userName}
              className="w-20 h-20 rounded-full mx-auto shadow-soft"
            />
            <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-success rounded-full border-2 border-card flex items-center justify-center">
              <div className="w-2 h-2 bg-card rounded-full"></div>
            </div>
          </div>
          <h2 className="text-xl font-medium text-foreground">
            Hi {userName} 👋
          </h2>
          <p className="text-muted-foreground mt-2">
            Ready for your daily check-in?
          </p>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button
            onClick={onStartSession}
            className="w-full h-12 text-lg font-medium bg-primary hover:bg-primary/90 
                     shadow-soft transition-smooth rounded-xl"
          >
            Start Session
          </Button>

          <div className="flex space-x-2">
            {onBackToLogin && (
              <Button
                onClick={onBackToLogin}
                variant="outline"
                className="flex-1 h-10 text-sm font-medium border-primary/30 hover:bg-primary/10 
                         hover:border-primary/50 transition-smooth rounded-xl"
              >
                Back to Home
              </Button>
            )}
            <Button
              onClick={onLogout}
              variant="outline"
              className="flex-1 h-10 text-sm font-medium border-destructive/30 hover:bg-destructive/10 
                       hover:border-destructive/50 text-destructive transition-smooth rounded-xl"
            >
              Logout
            </Button>
          </div>
        </div>

        <p className="text-xs text-muted-foreground mt-4">
          Your session is private and secure
        </p>
      </Card>
    </div>
  );
};