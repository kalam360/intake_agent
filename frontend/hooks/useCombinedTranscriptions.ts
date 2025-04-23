import { useTrackTranscription, useVoiceAssistant } from "@livekit/components-react";
import { useCallback, useMemo, useState } from "react";
import useLocalMicTrack from "./useLocalMicTrack";

export interface TranscriptionSegment {
  id: string;
  text: string;
  role: "assistant" | "user";
  firstReceivedTime: number;
}

export default function useCombinedTranscriptions() {
  const { agentTranscriptions } = useVoiceAssistant();
  const micTrackRef = useLocalMicTrack();
  const { segments: userTranscriptions } = useTrackTranscription(micTrackRef);
  
  // State to store manual text messages
  const [manualMessages, setManualMessages] = useState<TranscriptionSegment[]>([]);

  // Function to add a manual text message
  const addManualMessage = useCallback((text: string, role: "assistant" | "user" = "user") => {
    const newMessage: TranscriptionSegment = {
      id: `manual-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      text,
      role,
      firstReceivedTime: Date.now(),
    };
    
    setManualMessages((prev) => [...prev, newMessage]);
  }, []);

  const combinedTranscriptions = useMemo(() => {
    return [
      ...agentTranscriptions.map((val) => {
        return { ...val, role: "assistant" };
      }),
      ...userTranscriptions.map((val) => {
        return { ...val, role: "user" };
      }),
      ...manualMessages,
    ].sort((a, b) => a.firstReceivedTime - b.firstReceivedTime);
  }, [agentTranscriptions, userTranscriptions, manualMessages]);

  return {
    combinedTranscriptions,
    addManualMessage,
  };
}
