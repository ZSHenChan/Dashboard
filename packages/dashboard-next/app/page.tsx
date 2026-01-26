"use client";
import { useEffect, useState } from "react";
import Dashboard from "./components/dashboard/dashboard";

export default function Home() {
  // We store the colors as an object, not a class string.
  // This allows the style={} prop to handle the smooth transition.
  // const [gradientColors, setGradientColors] = useState({
  //   from: "#0f172a",
  //   via: "#1e293b",
  //   to: "#000000",
  // });

  // useEffect(() => {
  //   const updateTimeBackground = () => {
  //     const hour = new Date().getHours();

  //     // We use Hex codes here to ensure CSS can interpolate them perfectly.
  //     // You can grab these hex codes from the Tailwind color palette.
  //     if (hour >= 5 && hour < 6) {
  //       // Dawn: Pink to Orange
  //       setGradientColors({ from: "#ec4899", via: "#ef4444", to: "#f97316" });
  //     } else if (hour >= 6 && hour < 7) {
  //       // Morning: Indigo to Orange
  //       setGradientColors({ from: "#818cf8", via: "#d8b4fe", to: "#fdba74" });
  //     } else if (hour >= 7 && hour < 18) {
  //       // Day: Blue Sky
  //       setGradientColors({ from: "#fed7aa", via: "#a5f3fc", to: "#60a5fa" });
  //     } else if (hour >= 18 && hour < 20) {
  //       // Sunset: Purple to Orange
  //       setGradientColors({ from: "#3730a3", via: "#9333ea", to: "#fb923c" });
  //     } else {
  //       // Night: Dark Slate/Black
  //       setGradientColors({ from: "#0f172a", via: "#1e293b", to: "#000000" });
  //     }
  //   };

  //   updateTimeBackground();
  //   const interval = setInterval(updateTimeBackground, 60000);
  //   return () => clearInterval(interval);
  // }, []);

  return (
    <div className="flex min-h-screen items-center justify-center font-sans transition-all duration-[3000ms] ease-in-out animate-gradient linear-gradient(to bottom, rgba(9,21,45,1) 0%,rgba(28,30,147,1) 53%,rgba(83,101,155,1) 100%)">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-start py-32 px-4 sm:px-16">
        <h1 className="text-4xl font-bold text-white/90 mb-8 drop-shadow-md">
          My Dashboard
        </h1>
        <Dashboard />
      </main>
    </div>
  );
}
