import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import employeeAvatar from "@/assets/employee-avatar.jpg";
import ruhaniLogo from "@/assets/ruhani-logo.png";

interface EmployeeWelcomeProps {
  userName?: string;
  onStartSession: () => void;
}

export const EmployeeWelcome = ({ 
  userName = "Alex", 
  onStartSession 
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

        {/* Start Button */}
        <Button
          onClick={onStartSession}
          className="w-full h-12 text-lg font-medium bg-primary hover:bg-primary/90 
                     shadow-soft transition-smooth rounded-xl"
        >
          Start Session
        </Button>

        <p className="text-xs text-muted-foreground mt-4">
          Your session is private and secure
        </p>
      </Card>
    </div>
  );
};