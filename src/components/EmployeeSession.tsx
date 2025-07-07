import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { useEmployeeApi } from "@/hooks/useEmployeeApi";

interface EmployeeSessionProps {
  employeeId: string;
  onSessionComplete: () => void;
  onBackToWelcome?: () => void;
}

const moodEmojis = [
  { emoji: "😞", label: "Very Sad", value: 1 },
  { emoji: "😕", label: "Sad", value: 2 },
  { emoji: "😐", label: "Neutral", value: 3 },
  { emoji: "🙂", label: "Happy", value: 4 },
  { emoji: "😊", label: "Very Happy", value: 5 },
];

export const EmployeeSession = ({ employeeId, onSessionComplete, onBackToWelcome }: EmployeeSessionProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const [selectedMood, setSelectedMood] = useState<number | null>(null);
  const [waveAnimation, setWaveAnimation] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionResult, setSessionResult] = useState<any>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const { toast } = useToast();
  const { processVoiceSession } = useEmployeeApi();

  useEffect(() => {
    if (isRecording) {
      setWaveAnimation(true);
      // Auto-stop recording after 30 seconds for demo
      const timer = setTimeout(() => {
        handleStopRecording();
      }, 30000);
      return () => clearTimeout(timer);
    }
  }, [isRecording]);

  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      toast({
        title: "Microphone Access Required",
        description: "Please allow microphone access to start recording.",
        variant: "destructive"
      });
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setWaveAnimation(false);
    }
  };

  const handleComplete = async () => {
    if (!selectedMood) {
      toast({
        title: "Mood Rating Required",
        description: "Please select your mood before completing the session.",
        variant: "destructive"
      });
      return;
    }

    if (!audioBlob) {
      toast({
        title: "Voice Recording Required",
        description: "Please record your voice before completing the session.",
        variant: "destructive"
      });
      return;
    }

    setIsProcessing(true);

    try {
      // Convert audio blob to base64
      const arrayBuffer = await audioBlob.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

      const result = await processVoiceSession.mutateAsync({
        employee_id: employeeId,
        audio_data: base64Audio,
        mood_rating: selectedMood.toString()
      });

      if (result.success) {
        setSessionResult(result);
        toast({
          title: "Session Complete",
          description: "Your wellness session has been processed successfully.",
        });
        onSessionComplete();
      } else {
        toast({
          title: "Session Failed",
          description: "There was an issue processing your session. Please try again.",
          variant: "destructive"
        });
      }
    } catch (error) {
      toast({
        title: "Session Error",
        description: "An error occurred while processing your session.",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
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
          
          {audioBlob && (
            <p className="text-xs text-success mt-2">
              ✓ Voice recorded successfully
            </p>
          )}
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

        {/* Action Buttons */}
        <div className="space-y-3">
          <Button
            onClick={handleComplete}
            disabled={!selectedMood || !audioBlob || isProcessing}
            className="w-full h-12 text-lg font-medium bg-success hover:bg-success/90 
                     shadow-soft transition-smooth rounded-xl disabled:opacity-50"
          >
            {isProcessing ? "Processing Session..." : "Complete Check-in"}
          </Button>

          {onBackToWelcome && (
            <Button
              onClick={onBackToWelcome}
              variant="outline"
              className="w-full h-10 text-sm font-medium border-primary/30 hover:bg-primary/10 
                       hover:border-primary/50 transition-smooth rounded-xl"
            >
              Back to Welcome
            </Button>
          )}
        </div>

        <p className="text-xs text-muted-foreground mt-4">
          Your responses help us better support you
        </p>
      </Card>
    </div>
  );
};