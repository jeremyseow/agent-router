"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, Image, Database, LayoutDashboard } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

const navItems = [
    { name: "Chat", href: "/chat", icon: MessageSquare },
    { name: "Images", href: "/images", icon: Image },
    { name: "Ingestion", href: "/ingest", icon: Database },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="flex h-full w-64 flex-col glass border-r border-border min-h-screen">
            <div className="flex h-20 items-center px-6">
                <Link href="/" className="flex items-center gap-2 group">
                    <div className="h-8 w-8 rounded-lg bg-accent flex items-center justify-center shadow-lg shadow-accent/20 transition-transform group-hover:scale-110">
                        <LayoutDashboard className="h-5 w-5 text-accent-foreground" />
                    </div>
                    <span className="text-xl font-bold tracking-tight text-foreground">Agent Router</span>
                </Link>
            </div>

            <nav className="flex-1 space-y-1 px-3 py-4">
                {navItems.map((item) => {
                    const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "group relative flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200",
                                isActive
                                    ? "text-foreground bg-white/5"
                                    : "text-muted-foreground hover:text-foreground hover:bg-white/5"
                            )}
                        >
                            <item.icon className={cn(
                                "h-5 w-5 transition-colors duration-200",
                                isActive ? "text-accent" : "text-muted-foreground group-hover:text-foreground"
                            )} />
                            {item.name}

                            {isActive && (
                                <motion.div
                                    layoutId="active-pill"
                                    className="absolute left-0 h-8 w-1 rounded-r-full bg-accent"
                                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                />
                            )}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 mt-auto border-t border-border/50">
                <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 border border-white/5">
                    <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-accent to-blue-400 flex items-center justify-center text-xs font-bold">
                        JS
                    </div>
                    <div className="flex flex-col min-w-0">
                        <span className="text-sm font-medium truncate">Jeremy Seow</span>
                        <span className="text-[10px] text-muted-foreground uppercase tracking-wider">Administrator</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
