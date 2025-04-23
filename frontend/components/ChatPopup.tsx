"use client";

import { RoomAudioRenderer, useVoiceAssistant, RoomProvider } from "@livekit/components-react";
import { useCallback, useState, useEffect, useContext } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import TranscriptionView from "./TranscriptionView";
import ControlBar from "./ControlBar";
import useCombinedTranscriptions from "@/hooks/useCombinedTranscriptions";
import { NoAgentNotification } from "./NoAgentNotification";
import { Mic, MicOff, Send } from "lucide-react";
import { Room } from "livekit-client";
import { RoomContext } from "@livekit/components-react";
import type { ConnectionDetails } from "@/app/api/connection-details/route";
import ModeToggle from "./ModeToggle";
import { useAgentStore } from "@/store/agentStore";

export default function ChatPopup() {
  const { state: agentState } = useVoiceAssistant();
  const { addManualMessage } = useCombinedTranscriptions();
  const [message, setMessage] = useState("");
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const room = useContext(RoomContext) as Room | null;
  
  // Get state from Zustand store
  const { 
    mode, 
    conversationHistory, 
    sendTextMessage, 
    initialize,
    connectionDetails
  } = useAgentStore();

  // Initialize the agent when component mounts
  useEffect(() => {
    initialize();
  }, [initialize]);

  const handleSendMessage = () => {
    if (message.trim()) {
      if (mode === 'text') {
        // Send message to text agent
        sendTextMessage(message);
      } else {
        // Send message to voice agent
        addManualMessage(message);
      }
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  const toggleVoice = useCallback(async () => {
    if (!room) return;
    
    if (isVoiceActive) {
      await room.localParticipant.setMicrophoneEnabled(false);
      setIsVoiceActive(false);
    } else {
      if (agentState === "disconnected") {
        if (connectionDetails) {
          // Use connection details from store (when switching from text to voice)
          await room.connect(connectionDetails.url, connectionDetails.token);
        } else {
          // Get new connection details
          const url = new URL(
            process.env.NEXT_PUBLIC_CONN_DETAILS_ENDPOINT ?? "/api/connection-details",
            window.location.origin
          );
          const response = await fetch(url.toString());
          const connectionDetailsData: ConnectionDetails = await response.json();
          
          await room.connect(connectionDetailsData.serverUrl, connectionDetailsData.participantToken);
        }
      }
      
      await room.localParticipant.setMicrophoneEnabled(true);
      setIsVoiceActive(true);
    }
  }, [room, agentState, isVoiceActive, connectionDetails]);

  // Render text conversation history
  const renderTextConversation = () => {
    return (
      <div className="flex flex-col space-y-4">
        {conversationHistory.map((msg, index) => (
          <div 
            key={index} 
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                msg.role === 'user' 
                  ? 'bg-primary text-primary-foreground' 
                  : 'bg-muted'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-[500px] max-h-[80vh] w-full max-w-md">
      <div className="flex justify-between items-center p-2 border-b">
        <h3 className="font-medium">Real Estate Assistant</h3>
        <ModeToggle />
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 bg-background">
        {mode === 'text' ? (
          renderTextConversation()
        ) : (
          <TranscriptionView />
        )}
      </div>

      {mode === 'voice' && (
        <>
          <RoomAudioRenderer />
          <NoAgentNotification state={agentState} />

          {agentState !== "disconnected" && (
            <div className="py-2 px-4 border-t">
              <ControlBar />
            </div>
          )}
        </>
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
        
        {mode === 'voice' && (
          <Button
            variant="outline"
            size="icon"
            onClick={toggleVoice}
            className={isVoiceActive ? "bg-primary text-primary-foreground" : ""}
          >
            {isVoiceActive ? <Mic className="h-4 w-4" /> : <MicOff className="h-4 w-4" />}
          </Button>
        )}
      </div>
    </div>
  );
}
