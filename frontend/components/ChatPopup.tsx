"use client";

import { RoomAudioRenderer, useVoiceAssistant } from "@livekit/components-react";
import { useCallback, useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import TranscriptionView from "./TranscriptionView";
import ControlBar from "./ControlBar";
import useCombinedTranscriptions from "@/hooks/useCombinedTranscriptions";
import { NoAgentNotification } from "./NoAgentNotification";
import { Mic, MicOff, Send } from "lucide-react";
import { Room } from "livekit-client";
import { useContext } from "react";
import { RoomContext } from "@livekit/components-react";
import type { ConnectionDetails } from "@/app/api/connection-details/route";

export default function ChatPopup() {
  const { state: agentState } = useVoiceAssistant();
  const { addManualMessage } = useCombinedTranscriptions();
  const [message, setMessage] = useState("");
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const room = useContext(RoomContext) as Room;

  const handleSendMessage = () => {
    if (message.trim()) {
      addManualMessage(message);
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  const toggleVoice = useCallback(async () => {
    if (isVoiceActive) {
      await room.localParticipant.setMicrophoneEnabled(false);
      setIsVoiceActive(false);
    } else {
      if (agentState === "disconnected") {
        const url = new URL(
          process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT ?? "/api/connection-details",
          window.location.origin
        );
        const response = await fetch(url.toString());
        const connectionDetailsData: ConnectionDetails = await response.json();
        
        await room.connect(connectionDetailsData.serverUrl, connectionDetailsData.participantToken);
      }
      
      await room.localParticipant.setMicrophoneEnabled(true);
      setIsVoiceActive(true);
    }
  }, [room, agentState, isVoiceActive]);

  return (
    <div className="flex flex-col h-[500px] max-h-[80vh] w-full max-w-md">
      <div className="flex-1 overflow-hidden p-4 bg-background">
        <TranscriptionView />
      </div>

      <RoomAudioRenderer />
      <NoAgentNotification state={agentState} />

      {agentState !== "disconnected" && (
        <div className="py-2 px-4 border-t">
          <ControlBar />
        </div>
      )}

      <div className="p-4 border-t flex items-center gap-2">
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          className="flex-1"
        />
        <Button size="icon" onClick={handleSendMessage}>
          <Send className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={toggleVoice}
          className={isVoiceActive ? "bg-primary text-primary-foreground" : ""}
        >
          {isVoiceActive ? <Mic className="h-4 w-4" /> : <MicOff className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  );
}