import React from 'react';
import { Button } from './ui/button';
import { useAgentStore } from '../store/agentStore';
import { Mic, MessageSquare } from 'lucide-react';

export const ModeToggle: React.FC = () => {
  const { mode, isTransitioning, switchMode } = useAgentStore();
  
  const handleToggle = async () => {
    const newMode = mode === 'text' ? 'voice' : 'text';
    await switchMode(newMode);
  };
  
  return (
    <Button
      onClick={handleToggle}
      disabled={isTransitioning}
      variant="outline"
      size="sm"
      className="flex items-center gap-2"
      aria-label={`Switch to ${mode === 'text' ? 'voice' : 'text'} mode`}
    >
      {isTransitioning ? (
        <span className="flex items-center gap-2">
          <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></span>
          Switching...
        </span>
      ) : (
        <>
          {mode === 'text' ? (
            <>
              <Mic className="h-4 w-4" />
              Voice Mode
            </>
          ) : (
            <>
              <MessageSquare className="h-4 w-4" />
              Text Mode
            </>
          )}
        </>
      )}
    </Button>
  );
};

export default ModeToggle;
