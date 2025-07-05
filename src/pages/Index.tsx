import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmployeeApp } from "./EmployeeApp";
import { HRApp } from "./HRApp";
import ruhaniLogo from "@/assets/ruhani-logo.png";

type AppMode = "home" | "employee" | "hr";

const Index = () => {
  const [currentMode, setCurrentMode] = useState<AppMode>("home");

  if (currentMode === "employee") {
    return <EmployeeApp />;
  }

  if (currentMode === "hr") {
    return <HRApp />;
  }

  return (
    <div className="min-h-screen bg-gradient-wellness flex items-center justify-center p-4">
      <Card className="w-full max-w-lg p-8 text-center shadow-card border-0 bg-card/80 backdrop-blur-sm">
        {/* Logo */}
        <div className="mb-8">
          <img 
            src={ruhaniLogo} 
            alt="RUHANI" 
            className="w-32 h-32 mx-auto mb-6 animate-gentle-bounce"
          />
          <h1 className="text-4xl font-light text-foreground mb-3">RUHANI</h1>
          <p className="text-lg text-muted-foreground mb-2">
            Your Invisible AI Psychologist
          </p>
          <p className="text-sm text-muted-foreground/80">
            Supporting enterprise teams with compassionate wellness technology
          </p>
        </div>

        {/* Mode Selection */}
        <div className="space-y-4 mb-8">
          <Button
            onClick={() => setCurrentMode("employee")}
            className="w-full h-14 text-lg font-medium bg-primary hover:bg-primary/90 
                       shadow-soft transition-smooth rounded-xl group"
          >
            <div className="flex items-center justify-center space-x-3">
              <span>👤</span>
              <div className="text-left">
                <div>Employee Check-in</div>
                <div className="text-xs text-primary-foreground/80 font-normal">
                  Quick wellness session
                </div>
              </div>
            </div>
          </Button>

          <Button
            onClick={() => setCurrentMode("hr")}
            variant="outline"
            className="w-full h-14 text-lg font-medium border-primary/30 hover:bg-primary/10 
                       hover:border-primary/50 transition-smooth rounded-xl group"
          >
            <div className="flex items-center justify-center space-x-3">
              <span>📊</span>
              <div className="text-left">
                <div>HR Dashboard</div>
                <div className="text-xs text-muted-foreground font-normal">
                  Team wellness overview
                </div>
              </div>
            </div>
          </Button>
        </div>

        {/* Features */}
        <div className="space-y-3 mb-6">
          <div className="flex items-center space-x-3 text-sm text-muted-foreground">
            <div className="w-2 h-2 bg-success rounded-full"></div>
            <span>100% Private & Secure</span>
          </div>
          <div className="flex items-center space-x-3 text-sm text-muted-foreground">
            <div className="w-2 h-2 bg-primary rounded-full"></div>
            <span>HIPAA Compliant</span>
          </div>
          <div className="flex items-center space-x-3 text-sm text-muted-foreground">
            <div className="w-2 h-2 bg-warning rounded-full"></div>
            <span>AI-Powered Insights</span>
          </div>
        </div>

        <p className="text-xs text-muted-foreground/60">
          Mental wellness should be invisible until it's needed
        </p>
      </Card>
    </div>
  );
};

export default Index;
