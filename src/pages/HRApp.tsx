import { useState } from "react";
import { HRLogin } from "@/components/HRLogin";
import { HRDashboard } from "@/components/HRDashboard";

export const HRApp = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  if (isLoggedIn) {
    return <HRDashboard onLogout={handleLogout} />;
  }

  return <HRLogin onLogin={handleLogin} />;
};