import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import ruhaniLogo from "@/assets/ruhani-logo.png";

interface EmployeeCompleteProps {
  onNewSession: () => void;
  onLogout: () => void;
  onBackToWelcome?: () => void;
}

export const EmployeeComplete = ({ onNewSession, onLogout, onBackToWelcome }: EmployeeCompleteProps) => {
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
        </div>

        {/* Success Message */}
        <div className="mb-8">
          <div className="w-16 h-16 bg-success/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-medium text-foreground mb-2">
            Session Complete! 🎉
          </h2>
          <p className="text-muted-foreground">
            Thank you for sharing with me today. Your wellness matters.
          </p>
        </div>

        {/* Recommendations */}
        <div className="mb-8 p-4 bg-primary/10 rounded-lg border border-primary/20">
          <h3 className="text-sm font-medium text-foreground mb-2">Today's Wellness Tips:</h3>
          <ul className="text-sm text-muted-foreground space-y-1 text-left">
            <li>• Take a short walk outside</li>
            <li>• Practice deep breathing exercises</li>
            <li>• Stay hydrated throughout the day</li>
            <li>• Connect with a colleague or friend</li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button
            onClick={onNewSession}
            className="w-full h-12 text-lg font-medium bg-primary hover:bg-primary/90 
                     shadow-soft transition-smooth rounded-xl"
          >
            Start New Session
          </Button>

          <div className="flex space-x-2">
            {onBackToWelcome && (
              <Button
                onClick={onBackToWelcome}
                variant="outline"
                className="flex-1 h-10 text-sm font-medium border-primary/30 hover:bg-primary/10 
                         hover:border-primary/50 transition-smooth rounded-xl"
              >
                Back to Welcome
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
          Remember, I'm here whenever you need to talk
        </p>
      </Card>
    </div>
  );
};