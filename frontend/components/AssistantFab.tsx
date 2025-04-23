"use client";

import Image from "next/image";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogTrigger } from "./ui/dialog";
import ChatPopup from "./ChatPopup";

export default function AssistantFab() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg p-0 bg-primary hover:bg-primary/90"
          aria-label="Open assistant"
        >
          <Image
            src="/images/assistant-fab.svg"
            alt="Assistant"
            width={24}
            height={24}
            className="invert"
          />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md p-0 overflow-hidden">
        <ChatPopup />
      </DialogContent>
    </Dialog>
  );
}
