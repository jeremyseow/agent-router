"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Sparkles, User, Bot, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import { ChatResponse, Message } from "@/lib/api-types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ChatPage() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(null);

    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSubmit = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = input;
        setInput("");
        setMessages(prev => [...prev, { role: "user", content: userMessage }]);
        setIsLoading(true);

        try {
            const body: any = { message: userMessage };
            if (sessionId) body.session_id = sessionId;

            const res = await fetch(`${API_BASE}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });

            const data: ChatResponse = await res.json();

            if (data.session_id) setSessionId(data.session_id);

            setMessages(prev => [...prev, {
                role: "model",
                content: data.response
            }]);
        } catch (error) {
            setMessages(prev => [...prev, {
                role: "model",
                content: "Error: Could not connect to the orchestrator. Is the backend running?",
                isError: true
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full w-full">
            <header className="flex h-16 items-center justify-between border-b border-border/50 px-8 sticky top-0 bg-background/50 backdrop-blur-md z-10">
                <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-accent" />
                    <h1 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Orchestrator Chat</h1>
                </div>
                {sessionId && (
                    <div className="text-[10px] font-mono text-muted-foreground bg-white/5 px-2 py-1 rounded">
                        SID: {sessionId.slice(0, 8)}...
                    </div>
                )}
            </header>

            <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-10 scroll-smooth">
                <div className="max-w-4xl mx-auto space-y-8">
                    <AnimatePresence initial={false}>
                        {messages.length === 0 ? (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="flex flex-col items-center justify-center py-20 text-center"
                            >
                                <div className="h-20 w-20 rounded-3xl bg-accent/10 flex items-center justify-center mb-6 relative">
                                    <Bot className="h-10 w-10 text-accent" />
                                    <motion.div
                                        animate={{ scale: [1, 1.2, 1], opacity: [0.2, 0.5, 0.2] }}
                                        transition={{ repeat: Infinity, duration: 3 }}
                                        className="absolute inset-0 bg-accent rounded-3xl -z-10"
                                    />
                                </div>
                                <h2 className="text-3xl font-bold tracking-tight mb-3">Hello, Jeremy.</h2>
                                <p className="text-muted-foreground max-w-sm text-lg">
                                    I'm your AI Orchestrator. How can I assist you in coordinating your workers today?
                                </p>
                                <div className="grid grid-cols-2 gap-3 mt-10 w-full max-w-md">
                                    {["Research Bitcoin", "Write a Python script", "Check financial status", "Draft project plan"].map(suggestion => (
                                        <button
                                            key={suggestion}
                                            onClick={() => setInput(suggestion)}
                                            className="p-3 text-xs font-medium rounded-xl glass border border-white/5 hover:border-accent/40 transition-all text-muted-foreground hover:text-foreground text-left"
                                        >
                                            "{suggestion}..."
                                        </button>
                                    ))}
                                </div>
                            </motion.div>
                        ) : (
                            messages.map((msg, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, x: msg.role === "user" ? 20 : -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    className={cn(
                                        "flex gap-4 group",
                                        msg.role === "user" ? "flex-row-reverse" : "flex-row"
                                    )}
                                >
                                    <div className={cn(
                                        "h-10 w-10 rounded-xl flex items-center justify-center shrink-0 border border-white/5",
                                        msg.role === "user" ? "bg-accent/10 text-accent" : "bg-white/5 text-muted-foreground"
                                    )}>
                                        {msg.role === "user" ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
                                    </div>
                                    <div className={cn(
                                        "flex flex-col gap-2 max-w-[80%]",
                                        msg.role === "user" ? "items-end" : "items-start"
                                    )}>
                                        <div className={cn(
                                            "px-5 py-3 rounded-2xl glass text-sm leading-relaxed",
                                            msg.role === "user" ? "rounded-tr-none bg-accent/5 border-accent/10 text-foreground" : "rounded-tl-none border-white/5 text-muted-foreground",
                                            msg.isError && "border-red-500/50 bg-red-500/5 text-red-200"
                                        )}>
                                            {msg.content}
                                        </div>
                                    </div>
                                </motion.div>
                            ))
                        )}

                        {isLoading && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="flex gap-4"
                            >
                                <div className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center border border-white/5">
                                    <Loader2 className="h-5 w-5 animate-spin text-accent" />
                                </div>
                                <div className="px-5 py-3 rounded-2xl glass-accent rounded-tl-none text-sm text-accent italic">
                                    Orchestrator is thinking...
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            <div className="p-8 sticky bottom-0 bg-gradient-to-t from-background via-background/80 to-transparent">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-accent/50 to-blue-500/20 rounded-2xl opacity-0 group-focus-within:opacity-100 blur-md transition duration-500" />
                        <div className="relative glass rounded-2xl flex flex-col p-2">
                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        handleSubmit();
                                    }
                                }}
                                rows={1}
                                placeholder="Message the orchestrator..."
                                className="w-full bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground px-4 py-3 resize-none min-h-[56px] max-h-48"
                            />
                            <div className="flex items-center justify-between px-4 pb-2">
                                <div className="flex gap-2">
                                    <span className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Shift+Enter for new line</span>
                                </div>
                                <button
                                    disabled={isLoading || !input.trim()}
                                    className={cn(
                                        "h-10 w-10 rounded-xl flex items-center justify-center transition-all duration-300",
                                        input.trim() ? "bg-accent hover:scale-105 shadow-lg shadow-accent/20" : "bg-white/5 opacity-50 cursor-not-allowed"
                                    )}
                                >
                                    <Send className={cn("h-5 w-5 transition-transform", !isLoading && "group-hover:translate-x-0.5 group-hover:-translate-y-0.5")} />
                                </button>
                            </div>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
}
