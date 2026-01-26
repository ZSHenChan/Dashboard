"use client";
import { DashboardCard } from "./reply-types";
import { useEffect, useState } from "react";
import { EventCard } from "./event-card";

const SERVER_URL = "/api/proxy";

export default function Dashboard() {
  const [cards, setCards] = useState<DashboardCard[]>([]);

  // 1. Initial Load
  useEffect(() => {
    fetch(`${SERVER_URL}/user/notifications`)
      .then((res) => res.json())
      .then((data) => {
        setCards(data);
      })
      .catch((err) => console.error("Failed to load cards", err));
  }, []);

  // 2. Live Updates
  useEffect(() => {
    const eventSource = new EventSource(`${SERVER_URL}/user/stream`);

    eventSource.onmessage = (event) => {
      const newCard = JSON.parse(event.data);
      setCards((prev) => {
        if (prev.some((c) => c.id === newCard.id)) return prev;
        return [newCard, ...prev];
      });
    };

    return () => eventSource.close();
  }, []);

  // 3. Handle Action
  const handleAction = async (
    card: DashboardCard,
    action: string,
    text: string[] = [],
  ) => {
    if (action === "reply") {
      // 1. Send the instruction to FastAPI
      await fetch(`${SERVER_URL}/user/reply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: card.chat_id,
          text: text,
          card_id: card.id,
        }),
      });
    } else {
      // Handle ignore/delete normally
      await fetch(`${SERVER_URL}/user/notifications/${card.id}`, {
        method: "DELETE",
      });
    }

    // 2. Remove from UI
    setCards((prev) => prev.filter((c) => c.id !== card.id));
  };

  return (
    <>
      {cards.map((card: DashboardCard) => (
        <EventCard key={card.id} card={card} onAction={handleAction} />
      ))}
    </>
  );
}
