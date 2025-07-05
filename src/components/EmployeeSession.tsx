import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface EmployeeSessionProps {
  onSessionComplete: () => void;
}

const moodEmojis = [
  { emoji: "😞", label: "Very Sad", value: 1 },
  { emoji: "😕", label: "Sad", value: 2 },
  { emoji: "😐", label: "Neutral", value: 3 },
  { emoji: "🙂", label: "Happy", value: 4 },
  { emoji: "😊", label: "Very Happy", value: 5 },
];

export const EmployeeSession = ({ onSessionComplete }: EmployeeSessionProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [waveAnimation, setWaveAnimation] = useState(false);

  useEffect(() => {
    if (isRecording) {
      setWaveAnimation(true);
      // Auto-stop recording after 30 seconds for demo
      const timer = setTimeout(() => {
        setIsRecording(false);
        setWaveAnimation(false);
      }, 30000);
      return () => clearTimeout(timer);
    }
  }, [isRecording]);

  const handleStartRecording = () => {
    setIsRecording(true);
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    setWaveAnimation(false);
  };

  const handleComplete = () => {
    if (selectedMood) {
      onSessionComplete();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-wellness flex items-center justify-center p-4">
      <Card className="w-full max-w-lg p-8 text-center shadow-card border-0 bg-card/80 backdrop-blur-sm">
        {/* Header */}
        <div className="mb-8">
          <h2 className="text-2xl font-light text-foreground mb-2">
            How are you feeling today?
          </h2>
          <p className="text-muted-foreground">
            Share your thoughts - I'm here to listen
          </p>
        </div>

        {/* Voice Recording Section */}
        <div className="mb-8">
          <div className="relative mb-6">
            <div 
              className={`w-24 h-24 mx-auto rounded-full flex items-center justify-center
                         cursor-pointer transition-smooth shadow-soft
                         ${isRecording 
                           ? 'bg-destructive shadow-glow animate-pulse-soft' 
                           : 'bg-primary hover:bg-primary/90'
                         }`}
              onClick={isRecording ? handleStopRecording : handleStartRecording}
            >
              {isRecording ? (
                <div className="w-6 h-6 bg-card rounded-sm"></div>
              ) : (
                <svg className="w-8 h-8 text-primary-foreground" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
              )}
            </div>

            {/* Wave Animation */}
            {waveAnimation && (
              <div className="flex justify-center items-center mt-4 space-x-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-primary rounded-full animate-wave"
                    style={{
                      height: '20px',
                      animationDelay: `${i * 0.1}s`
                    }}
                  />
                ))}
              </div>
            )}
          </div>

          <p className="text-sm text-muted-foreground">
            {isRecording ? "Listening... Tap to stop" : "Tap to start sharing"}
          </p>
        </div>

        {/* Mood Selection */}
        <div className="mb-8">
          <p className="text-sm font-medium text-foreground mb-4">
            How would you rate your mood?
          </p>
          <div className="flex justify-center space-x-3">
            {moodEmojis.map((mood) => (
              <button
                key={mood.value}
                onClick={() => setSelectedMood(mood.value)}
                className={`text-3xl p-3 rounded-xl transition-smooth
                           ${selectedMood === mood.value 
                             ? 'bg-primary/20 shadow-soft scale-110' 
                             : 'hover:bg-muted/50 hover:scale-105'
                           }`}
                title={mood.label}
              >
                {mood.emoji}
              </button>
            ))}
          </div>
        </div>

        {/* Complete Button */}
        <Button
          onClick={handleComplete}
          disabled={!selectedMood && !isRecording}
          className="w-full h-12 text-lg font-medium bg-success hover:bg-success/90 
                     shadow-soft transition-smooth rounded-xl disabled:opacity-50"
        >
          Complete Check-in
        </Button>

        <p className="text-xs text-muted-foreground mt-4">
          Your responses help us better support you
        </p>
      </Card>
    </div>
  );
};