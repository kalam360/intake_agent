"use client";

import { RoomContext } from "@livekit/components-react";
import { Room, RoomEvent } from "livekit-client";
import { useCallback, useEffect, useState } from "react";
import ListingGrid from "@/components/ListingGrid";
import AssistantFab from "@/components/AssistantFab";

export default function Page() {
  const [room] = useState(new Room());

  useEffect(() => {
    room.on(RoomEvent.MediaDevicesError, onDeviceFailure);

    return () => {
      room.off(RoomEvent.MediaDevicesError, onDeviceFailure);
    };
  }, [room]);

  return (
    <main className="p-8 bg-background min-h-screen">
      <RoomContext.Provider value={room}>
        <h1 className="text-3xl font-bold mb-8">Featured Properties</h1>
        <ListingGrid />
        <AssistantFab />
      </RoomContext.Provider>
    </main>
  );
}

function onDeviceFailure(error: Error) {
  console.error(error);
  alert(
    "Error acquiring camera or microphone permissions. Please make sure you grant the necessary permissions in your browser and reload the tab"
  );
}
