import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface EmployeeCompleteProps {
  onNewSession: () => void;
}

export const EmployeeComplete = ({ onNewSession }: EmployeeCompleteProps) => {
  return (
    <div className="min-h-screen bg-gradient-wellness flex items-center justify-center p-4">
      <Card className="w-full max-w-md p-8 text-center shadow-card border-0 bg-card/80 backdrop-blur-sm">
        {/* Success Icon */}
        <div className="mb-6">
          <div className="w-20 h-20 mx-auto bg-success/20 rounded-full flex items-center justify-center mb-4">
            <svg className="w-10 h-10 text-success" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        </div>

        {/* Thank You Message */}
        <div className="mb-8">
          <h2 className="text-2xl font-light text-foreground mb-3">
            Thank you 💜
          </h2>
          <p className="text-muted-foreground leading-relaxed">
            Your check-in has been recorded securely. We'll take care of the rest and ensure you get the support you need.
          </p>
        </div>

        {/* Gentle Reminder */}
        <div className="mb-8 p-4 bg-primary/10 rounded-lg">
          <p className="text-sm text-foreground/80">
            Remember: You're not alone in this journey. We're here to support your wellbeing every step of the way.
          </p>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          <Button
            onClick={onNewSession}
            variant="outline"
            className="w-full h-11 font-medium border-primary/30 hover:bg-primary/10 
                       transition-smooth rounded-xl"
          >
            New Check-in
          </Button>
          
          <p className="text-xs text-muted-foreground">
            Next check-in available in 24 hours
          </p>
        </div>

        {/* Floating Hearts Animation */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="animate-float text-2xl opacity-20">💜</div>
          </div>
        </div>
      </Card>
    </div>
  );
};