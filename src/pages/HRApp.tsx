import { useState } from "react";
import { HRLogin } from "@/components/HRLogin";
import { HRDashboard } from "@/components/HRDashboard";

interface HRAppProps {
  onBackToHome?: () => void;
}

export const HRApp = ({ onBackToHome }: HRAppProps) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    if (onBackToHome) {
      onBackToHome();
    }
  };

  if (isLoggedIn) {
    return <HRDashboard onLogout={handleLogout} />;
  }

  return <HRLogin onLogin={handleLogin} onBackToHome={onBackToHome} />;
};