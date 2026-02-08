"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Settings, Library } from "lucide-react";
import { useState } from "react";

export function FloatingNav() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { name: "Home", href: "/", icon: <Home size={20} strokeWidth={1.5} /> },
    {
      name: "Prompt Library",
      href: "/prompt-library",
      icon: <Library size={20} strokeWidth={1.5} />,
    },
    {
      name: "Settings",
      href: "/settings",
      icon: <Settings size={20} strokeWidth={1.5} />,
    },
  ];

  return (
    <div
      // 1. Desktop Hover Logic: Open on mouse enter, Close on mouse leave
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
      className="fixed bottom-8 right-8 z-50 flex flex-col items-center gap-4"
    >
      {/* Expanded Menu Items */}
      <div
        className={`flex flex-col gap-3 mb-2 transition-all duration-300 ease-out origin-bottom ${
          isOpen
            ? "opacity-100 translate-y-0 scale-100 pointer-events-auto"
            : "opacity-0 translate-y-4 scale-95 pointer-events-none"
        }`}
      >
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              // 2. Close menu when a link is clicked (UX best practice)
              onClick={() => setIsOpen(false)}
              className="relative flex items-center justify-end group/item"
            >
              {/* Tooltip Label */}
              <span className="absolute right-10 px-2 py-1 text-xs font-medium text-white/80 bg-black/40 backdrop-blur-md rounded opacity-0 -translate-x-2 group-hover/item:opacity-100 group-hover/item:translate-x-0 transition-all duration-200 pointer-events-none whitespace-nowrap hidden sm:block">
                {item.name}
              </span>

              <div
                className={`p-3 rounded-full border transition-all duration-200 ${
                  isActive
                    ? "bg-white text-black border-white"
                    : "bg-black/20 text-white/70 border-white/20 hover:border-white/50 hover:text-white hover:bg-black/40 backdrop-blur-sm"
                }`}
              >
                {item.icon}
              </div>
            </Link>
          );
        })}
      </div>

      {/* The Anchor Trigger */}
      <button
        // 3. Mobile Logic: Toggle on click
        onClick={() => setIsOpen(!isOpen)}
        className="relative flex flex-col items-center justify-center gap-1.5 w-12 h-12 rounded-full border border-white/20 bg-white/5 backdrop-blur-md cursor-pointer hover:border-white/40 hover:bg-white/10 transition-colors shadow-lg outline-none"
      >
        <div
          className={`w-5 h-[1px] bg-white/80 transition-transform duration-300 ${
            isOpen ? "rotate-45 translate-y-[2.5px]" : ""
          }`}
        />
        <div
          className={`w-5 h-[1px] bg-white/80 transition-transform duration-300 ${
            isOpen ? "-rotate-45 -translate-y-[2.5px]" : ""
          }`}
        />
      </button>

      {/* Vertical Connecting Line */}
      <div
        className={`absolute bottom-6 w-[1px] bg-gradient-to-t from-white/20 to-transparent transition-all duration-500 delay-75 -z-10 ${
          isOpen ? "h-40" : "h-0"
        }`}
      />
    </div>
  );
}
