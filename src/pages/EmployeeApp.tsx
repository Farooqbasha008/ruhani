import { useState, useEffect } from "react";
import { EmployeeLogin } from "@/components/EmployeeLogin";
import { EmployeeOnboarding } from "@/components/EmployeeOnboarding";
import { EmployeeWelcome } from "@/components/EmployeeWelcome";
import { EmployeeSession } from "@/components/EmployeeSession";
import { EmployeeComplete } from "@/components/EmployeeComplete";

type EmployeeView = "login" | "onboarding" | "welcome" | "session" | "complete";

interface EmployeeAppProps {
  onBackToHome?: () => void;
}

export const EmployeeApp = ({ onBackToHome }: EmployeeAppProps) => {
  const [currentView, setCurrentView] = useState<EmployeeView>("login");
  const [employeeId, setEmployeeId] = useState<string | null>(null);
  const [employeeName, setEmployeeName] = useState<string>("");

  // Check if user is already logged in
  useEffect(() => {
    const storedEmployeeId = localStorage.getItem("employee_id");
    const storedName = localStorage.getItem("employee_name");
    
    if (storedEmployeeId) {
      setEmployeeId(storedEmployeeId);
      setEmployeeName(storedName || "Employee");
      setCurrentView("welcome");
    }
  }, []);

  const handleLoginSuccess = (newEmployeeId: string, newEmployeeName: string) => {
    setEmployeeId(newEmployeeId);
    setEmployeeName(newEmployeeName);
    setCurrentView("welcome");
  };

  const handleOnboardingComplete = (newEmployeeId: string) => {
    setEmployeeId(newEmployeeId);
    setCurrentView("welcome");
  };

  const handleShowOnboarding = () => {
    setCurrentView("onboarding");
  };

  const handleBackToLogin = () => {
    setCurrentView("login");
  };

  const handleBackToHome = () => {
    if (onBackToHome) {
      onBackToHome();
    } else {
      setCurrentView("login");
    }
  };

  const handleBackToWelcome = () => {
    setCurrentView("welcome");
  };

  const handleStartSession = () => {
    setCurrentView("session");
  };

  const handleSessionComplete = () => {
    setCurrentView("complete");
  };

  const handleNewSession = () => {
    setCurrentView("welcome");
  };

  const handleLogout = () => {
    localStorage.removeItem("employee_id");
    localStorage.removeItem("employee_name");
    localStorage.removeItem("jwt");
    setEmployeeId(null);
    setEmployeeName("");
    if (onBackToHome) {
      onBackToHome();
    } else {
      setCurrentView("login");
    }
  };

  switch (currentView) {
    case "login":
      return (
        <EmployeeLogin 
          onLoginSuccess={handleLoginSuccess}
          onShowOnboarding={handleShowOnboarding}
          onBackToHome={handleBackToHome}
        />
      );
    case "onboarding":
      return <EmployeeOnboarding onOnboardingComplete={handleOnboardingComplete} onBackToLogin={handleBackToLogin} onBackToHome={handleBackToHome} />;
    case "welcome":
      return (
        <EmployeeWelcome 
          userName={employeeName} 
          onStartSession={handleStartSession}
          onLogout={handleLogout}
          onBackToLogin={handleBackToHome}
        />
      );
    case "session":
      return (
        <EmployeeSession 
          employeeId={employeeId!}
          onSessionComplete={handleSessionComplete}
          onBackToWelcome={handleBackToWelcome}
        />
      );
    case "complete":
      return (
        <EmployeeComplete 
          onNewSession={handleNewSession}
          onLogout={handleLogout}
          onBackToWelcome={handleBackToWelcome}
        />
      );
    default:
      return (
        <EmployeeLogin 
          onLoginSuccess={handleLoginSuccess}
          onShowOnboarding={handleShowOnboarding}
          onBackToHome={handleBackToHome}
        />
      );
  }
};