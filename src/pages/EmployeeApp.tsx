import { useState } from "react";
import { EmployeeWelcome } from "@/components/EmployeeWelcome";
import { EmployeeSession } from "@/components/EmployeeSession";
import { EmployeeComplete } from "@/components/EmployeeComplete";

type EmployeeView = "welcome" | "session" | "complete";

export const EmployeeApp = () => {
  const [currentView, setCurrentView] = useState<EmployeeView>("welcome");

  const handleStartSession = () => {
    setCurrentView("session");
  };

  const handleSessionComplete = () => {
    setCurrentView("complete");
  };

  const handleNewSession = () => {
    setCurrentView("welcome");
  };

  switch (currentView) {
    case "welcome":
      return <EmployeeWelcome onStartSession={handleStartSession} />;
    case "session":
      return <EmployeeSession onSessionComplete={handleSessionComplete} />;
    case "complete":
      return <EmployeeComplete onNewSession={handleNewSession} />;
    default:
      return <EmployeeWelcome onStartSession={handleStartSession} />;
  }
};