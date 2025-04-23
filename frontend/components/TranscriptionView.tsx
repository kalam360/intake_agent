import useCombinedTranscriptions from "@/hooks/useCombinedTranscriptions";
import * as React from "react";

export interface TranscriptionViewProps {
  onAddMessage?: (message: string) => void;
}

export default function TranscriptionView({ onAddMessage }: TranscriptionViewProps) {
  const { combinedTranscriptions } = useCombinedTranscriptions();

  // scroll to bottom when new transcription is added
  React.useEffect(() => {
    const transcription = combinedTranscriptions[combinedTranscriptions.length - 1];
    if (transcription) {
      const transcriptionElement = document.getElementById(transcription.id);
      if (transcriptionElement) {
        transcriptionElement.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [combinedTranscriptions]);

  return (
    <div className="h-full flex flex-col gap-2 overflow-y-auto">
      {combinedTranscriptions.map((segment) => (
        <div
          id={segment.id}
          key={segment.id}
          className={
            segment.role === "assistant"
              ? "p-2 self-start fit-content bg-gray-100 dark:bg-gray-800 rounded-md"
              : "bg-primary text-primary-foreground rounded-md p-2 self-end fit-content"
          }
        >
          {segment.text}
        </div>
      ))}
    </div>
  );
}
