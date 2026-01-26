"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Settings, Library } from "lucide-react";

export function FloatingNav() {
  const pathname = usePathname();

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
    <div className="fixed bottom-8 right-8 z-50 flex flex-col items-center gap-4 group">
      {/* Expanded Menu Items (Hidden by default, slide up on hover) */}
      <div className="flex flex-col gap-3 mb-2 opacity-0 translate-y-4 scale-95 pointer-events-none group-hover:opacity-100 group-hover:translate-y-0 group-hover:scale-100 group-hover:pointer-events-auto transition-all duration-300 ease-out origin-bottom">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className="relative flex items-center justify-end group/item"
            >
              {/* Tooltip Label (Appears on hover of specific item) */}
              <span className="absolute right-10 px-2 py-1 text-xs font-medium text-white/80 bg-black/40 backdrop-blur-md rounded opacity-0 -translate-x-2 group-hover/item:opacity-100 group-hover/item:translate-x-0 transition-all duration-200 pointer-events-none whitespace-nowrap">
                {item.name}
              </span>

              {/* Icon Circle */}
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

      {/* The Anchor Trigger (The "Menu" Button) */}
      <div className="relative flex flex-col items-center justify-center gap-1.5 w-12 h-12 rounded-full border border-white/20 bg-white/5 backdrop-blur-md cursor-pointer hover:border-white/40 hover:bg-white/10 transition-colors shadow-lg">
        {/* Minimalist Hamburger Lines that turn into X */}
        <div className="w-5 h-[1px] bg-white/80 group-hover:rotate-45 group-hover:translate-y-[2.5px] transition-transform duration-300" />
        <div className="w-5 h-[1px] bg-white/80 group-hover:-rotate-45 group-hover:-translate-y-[2.5px] transition-transform duration-300" />
      </div>

      {/* Vertical Connecting Line (Optional Aesthetic) */}
      <div className="absolute bottom-6 w-[1px] h-0 bg-gradient-to-t from-white/20 to-transparent group-hover:h-40 transition-all duration-500 delay-75 -z-10" />
    </div>
  );
}
