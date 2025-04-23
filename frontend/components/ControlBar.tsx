"use client";

import { useKrispNoiseFilter } from "@livekit/components-react/krisp";
import {
  BarVisualizer,
  DisconnectButton,
  VoiceAssistantControlBar,
  useVoiceAssistant,
} from "@livekit/components-react";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect } from "react";
import { CloseIcon } from "./CloseIcon";

export default function ControlBar() {
  /**
   * Use Krisp background noise reduction when available.
   * Note: This is only available on Scale plan, see {@link https://livekit.io/pricing | LiveKit Pricing} for more details.
   */
  const krisp = useKrispNoiseFilter();
  useEffect(() => {
    krisp.setNoiseFilterEnabled(true);
  }, []); // Empty dependency array to run only once

  const { state: agentState, audioTrack } = useVoiceAssistant();

  if (agentState === "disconnected" || agentState === "connecting") {
    return null;
  }

  return (
    <div className="relative h-[60px]">
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0, top: "10px" }}
          animate={{ opacity: 1, top: 0 }}
          exit={{ opacity: 0, top: "-10px" }}
          transition={{ duration: 0.4, ease: [0.09, 1.04, 0.245, 1.055] }}
          className="flex absolute w-full h-full justify-between px-8 sm:px-4"
        >
          <BarVisualizer
            state={agentState}
            barCount={5}
            trackRef={audioTrack}
            className="agent-visualizer w-24 gap-2"
            options={{ minHeight: 12 }}
          />
          <div className="flex items-center">
            <VoiceAssistantControlBar controls={{ leave: false }} />
            <DisconnectButton>
              <CloseIcon />
            </DisconnectButton>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}