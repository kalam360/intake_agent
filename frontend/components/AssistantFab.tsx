"use client";

import { useTheme } from "next-themes";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogTrigger } from "./ui/dialog";
import ChatPopup from "./ChatPopup";
import { useEffect, useState } from "react";
import Image from "next/image";

export default function AssistantFab() {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          className="fixed bottom-6 right-6 h-32 w-32 rounded-full shadow-lg p-0 bg-transparent hover:bg-transparent/10"
          aria-label="Open assistant"
        >
          {mounted && (
            <Image 
              src="/images/assistant-fab.min.svg"
              alt="Assistant"
              width={64}
              height={64}
              className="text-primary-foreground"
            />
          )}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md p-0 overflow-hidden">
        <ChatPopup />
      </DialogContent>
    </Dialog>
  );
}
