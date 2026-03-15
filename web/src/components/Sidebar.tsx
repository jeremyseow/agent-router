"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, Image, Database, LayoutDashboard, ChevronLeft, ChevronRight, Menu, X, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

const navItems = [
    { name: "Chat", href: "/chat", icon: MessageSquare },
    { name: "Images", href: "/images", icon: Image },
    { name: "Ingestion", href: "/ingest", icon: Database },
];

export function Sidebar() {
    const pathname = usePathname();
    const [isCollapsed, setIsCollapsed] = useState(false);
    const [isMobileOpen, setIsMobileOpen] = useState(false);
    const [isMobile, setIsMobile] = useState(false);

    // Responsive detection
    useEffect(() => {
        const checkMobile = () => {
            const mobile = window.innerWidth < 1024;
            setIsMobile(mobile);
            if (!mobile) setIsMobileOpen(false);
        };
        checkMobile();
        window.addEventListener("resize", checkMobile);
        return () => window.removeEventListener("resize", checkMobile);
    }, []);

    // Close mobile sidebars on navigation
    useEffect(() => {
        setIsMobileOpen(false);
    }, [pathname]);

    const sidebarContent = (
        <div className={cn(
            "flex h-full flex-col bg-zinc-950 border-r border-white/5 transition-all duration-300 ease-in-out relative",
            isCollapsed && !isMobile ? "w-20" : "w-64"
        )}>
            {/* Logo & Toggle Section */}
            <div className={cn(
                "flex h-20 items-center px-6 mb-2",
                isCollapsed && !isMobile ? "justify-center" : "justify-between"
            )}>
                <div className="flex items-center gap-3 overflow-hidden">
                    <button
                        onClick={() => setIsCollapsed(!isCollapsed)}
                        className={cn(
                            "h-10 w-10 shrink-0 flex items-center justify-center rounded-xl hover:bg-white/5 transition-colors text-muted-foreground hover:text-foreground",
                            isMobile && "hidden" // Mobile uses the fixed burger
                        )}
                    >
                        <Menu className="h-5 w-5" />
                    </button>
                    {!isCollapsed && !isMobile && (
                        <Link href="/" className="flex items-center gap-2 group">
                            <div className="h-8 w-8 rounded-lg bg-accent flex items-center justify-center shadow-lg shadow-accent/20 transition-transform group-hover:scale-105">
                                <LayoutDashboard className="h-5 w-5 text-accent-foreground" />
                            </div>
                            <span className="text-lg font-bold tracking-tight text-foreground whitespace-nowrap">
                                Agent Router
                            </span>
                        </Link>
                    )}
                </div>
                
                {isMobile && (
                    <button onClick={() => setIsMobileOpen(false)} className="text-muted-foreground hover:text-foreground">
                        <X className="h-6 w-6" />
                    </button>
                )}
            </div>

            {/* Collapsed Logo - shown only when collapsed on desktop */}
            {isCollapsed && !isMobile && (
                <div className="flex justify-center mb-6">
                    <Link href="/" className="h-10 w-10 rounded-xl bg-accent flex items-center justify-center shadow-lg shadow-accent/20">
                        <LayoutDashboard className="h-6 w-6 text-accent-foreground" />
                    </Link>
                </div>
            )}

            {/* Navigation */}
            <nav className="flex-1 space-y-2 px-3">
                {navItems.map((item) => {
                    const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "group relative flex items-center rounded-xl p-3 text-sm font-medium transition-all duration-200",
                                isCollapsed && !isMobile ? "justify-center" : "gap-3 px-4",
                                isActive
                                    ? "text-foreground bg-accent/10 border border-accent/20"
                                    : "text-muted-foreground hover:text-foreground hover:bg-white/5 border border-transparent"
                            )}
                        >
                            <item.icon className={cn(
                                "h-5 w-5 transition-colors duration-200",
                                isActive ? "text-accent" : "text-muted-foreground group-hover:text-foreground"
                            )} />
                            
                            {(!isCollapsed || isMobile) && (
                                <span className="whitespace-nowrap">{item.name}</span>
                            )}

                            {isActive && !isCollapsed && (
                                <motion.div
                                    layoutId="active-pill"
                                    className="absolute left-0 h-6 w-1 rounded-r-full bg-accent"
                                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                />
                            )}

                            {/* Tooltip for collapsed state */}
                            {isCollapsed && !isMobile && (
                                <div className="absolute left-full ml-4 px-3 py-1 bg-zinc-800 text-white text-[10px] rounded-md opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 whitespace-nowrap border border-white/5">
                                    {item.name}
                                </div>
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Profile Section */}
            <div className="p-4 mt-auto border-t border-white/5">
                <div className={cn(
                    "flex items-center rounded-2xl bg-white/5 border border-white/5 p-2 transition-all",
                    isCollapsed && !isMobile ? "justify-center" : "gap-3 px-3"
                )}>
                    <div className="h-10 w-10 shrink-0 rounded-xl bg-gradient-to-tr from-accent to-blue-500 flex items-center justify-center text-xs font-bold shadow-lg">
                        JS
                    </div>
                    {(!isCollapsed || isMobile) && (
                        <div className="flex flex-col min-w-0 overflow-hidden">
                            <span className="text-sm font-semibold truncate">Jeremy Seow</span>
                            <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Admin</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );

    return (
        <>
            {/* Burger Button for Mobile */}
            {isMobile && (
                <div className="fixed top-4 left-4 z-[60]">
                    <button
                        onClick={() => setIsMobileOpen(true)}
                        className="h-10 w-10 flex items-center justify-center rounded-xl bg-zinc-900 border border-white/10 shadow-2xl text-accent active:scale-95 transition-transform"
                    >
                        <Menu className="h-6 w-6" />
                    </button>
                </div>
            )}

            {/* Backdrop for Mobile */}
            <AnimatePresence>
                {isMobile && isMobileOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setIsMobileOpen(false)}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[70] lg:hidden"
                    />
                )}
            </AnimatePresence>

            {/* Sidebar View */}
            {isMobile ? (
                <AnimatePresence>
                    {isMobileOpen && (
                        <motion.div
                            initial={{ x: "-100%" }}
                            animate={{ x: 0 }}
                            exit={{ x: "-100%" }}
                            transition={{ type: "spring", damping: 25, stiffness: 200 }}
                            className="fixed inset-y-0 left-0 z-[80] shadow-2xl"
                        >
                            {sidebarContent}
                        </motion.div>
                    )}
                </AnimatePresence>
            ) : (
                sidebarContent
            )}
        </>
    );
}
