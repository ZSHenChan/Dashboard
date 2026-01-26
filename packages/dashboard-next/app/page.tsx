"use client";
import { useEffect, useState } from "react";
import Dashboard from "./components/dashboard";

export default function Home() {
  const [gradient, setGradient] = useState(
    "bg-gradient-to-br from-blue-900 to-black",
  ); // Default night

  useEffect(() => {
    const updateTimeBackground = () => {
      const hour = new Date().getHours();

      // Define time ranges and gradients
      if (hour >= 5 && hour < 6) {
        // Dawn: Soft orange to light blue
        setGradient("bg-linear-to-r from-pink-500 via-red-500 to-orange-500");
      } else if (hour >= 6 && hour < 7) {
        // Dawn: Soft orange to light blue
        setGradient(
          "bg-gradient-to-br from-indigo-400 via-purple-300 to-orange-200",
        );
      } else if (hour >= 7 && hour < 17) {
        // Day: Bright blue sky
        setGradient(
          "bg-linear-to-br from-orange-200 via-cyan-200 via-blue-300 to-blue-400",
        );
      } else if (hour >= 17 && hour < 20) {
        // Sunset: Deep purple to fiery orange
        setGradient(
          "bg-gradient-to-br from-indigo-800 via-purple-600 to-orange-400",
        );
      } else {
        // Night: Deep blues and black
        setGradient("bg-gradient-to-br from-slate-800 via-slate-900 to-black");
      }
    };

    updateTimeBackground();
    // Check every minute to update background if the hour changes
    const interval = setInterval(updateTimeBackground, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    // formatting: transition-colors ensures the background changes smoothly rather than snapping
    <div
      className={`flex min-h-screen items-center justify-center font-sans transition-all duration-1000 ease-in-out ${gradient}`}
    >
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-start py-32 px-4 sm:px-16">
        <h1 className="text-4xl font-bold text-white/90 mb-8 drop-shadow-md">
          My Dashboard
        </h1>
        <Dashboard />
      </main>
    </div>
  );
}
