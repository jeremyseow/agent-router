"use client";

import { useState, useRef } from "react";
import { Upload, Image as ImageIcon, Send, Loader2, X, Download } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ImagesPage() {
    const [prompt, setPrompt] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            if (selectedFile.size > 4 * 1024 * 1024) {
                setError("File too large. Max 4MB.");
                return;
            }
            setFile(selectedFile);
            setPreviewUrl(URL.createObjectURL(selectedFile));
            setError(null);
        }
    };

    const removeFile = () => {
        setFile(null);
        if (previewUrl) URL.revokeObjectURL(previewUrl);
        setPreviewUrl(null);
    };

    const handleSubmit = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!prompt.trim() || isLoading) return;

        setIsLoading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append("prompt", prompt);
            if (file) {
                formData.append("reference_image", file);
            }

            const res = await fetch(`${API_BASE}/images/generate`, {
                method: "POST",
                body: formData,
            });

            if (!res.ok) throw new Error("Generation failed");

            const blob = await res.blob();
            const imageUrl = URL.createObjectURL(blob);
            setGeneratedImage(imageUrl);
        } catch (err) {
            setError("Failed to generate image. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full w-full">
            <header className="flex h-16 items-center border-b border-border/50 px-8 sticky top-0 bg-background/50 backdrop-blur-md z-10">
                <div className="flex items-center gap-2">
                    <ImageIcon className="h-4 w-4 text-accent" />
                    <h1 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Image Generation</h1>
                </div>
            </header>

            <div className="flex-1 overflow-y-auto px-8 py-10">
                <div className="max-w-4xl mx-auto space-y-12">

                    <AnimatePresence mode="wait">
                        {!generatedImage ? (
                            <motion.div
                                key="empty"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="flex flex-col items-center justify-center py-20 text-center opacity-50 grayscale"
                            >
                                <div className="h-32 w-32 rounded-full bg-white/5 flex items-center justify-center mb-6 border border-white/5">
                                    <ImageIcon className="h-12 w-12 text-muted-foreground" />
                                </div>
                                <h2 className="text-2xl font-bold tracking-tight mb-2">Create something visual.</h2>
                                <p className="text-muted-foreground max-w-sm">
                                    Describe what you want to see, or upload a reference image to guide the generation.
                                </p>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="generated"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="relative group rounded-3xl overflow-hidden glass border-white/10 shadow-2xl"
                            >
                                <img src={generatedImage} alt="Generated" className="w-full h-auto object-cover max-h-[70vh]" />
                                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-8">
                                    <div className="flex items-center justify-between w-full">
                                        <p className="text-sm text-white/80 line-clamp-2 max-w-lg italic">"{prompt}"</p>
                                        <a
                                            href={generatedImage}
                                            download="generated-image.jpg"
                                            className="bg-white/10 hover:bg-white/20 p-3 rounded-xl backdrop-blur-md transition-all"
                                        >
                                            <Download className="h-5 w-5 text-white" />
                                        </a>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {error && (
                        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2">
                            <X className="h-4 w-4" />
                            {error}
                        </div>
                    )}

                </div>
            </div>

            <div className="p-8 sticky bottom-0 bg-gradient-to-t from-background via-background/80 to-transparent">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto space-y-4">

                    <div className="flex items-center gap-4">
                        <button
                            type="button"
                            onClick={() => fileInputRef.current?.click()}
                            className={cn(
                                "flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all group",
                                previewUrl
                                    ? "bg-accent/10 border border-accent/20 text-accent"
                                    : "bg-white/5 border border-white/5 text-muted-foreground hover:text-foreground hover:bg-white/10"
                            )}
                        >
                            <Upload className="h-4 w-4 transition-transform group-hover:-translate-y-0.5" />
                            {file ? "Change Reference" : "Upload Reference"}
                        </button>
                        <input
                            type="file"
                            className="hidden"
                            ref={fileInputRef}
                            accept="image/*"
                            onChange={handleFileChange}
                        />

                        <AnimatePresence>
                            {previewUrl && (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.8 }}
                                    className="relative h-10 w-10 rounded-lg overflow-hidden border border-accent/20"
                                >
                                    <img src={previewUrl} className="w-full h-full object-cover" />
                                    <button
                                        type="button"
                                        onClick={removeFile}
                                        className="absolute inset-0 bg-black/60 opacity-0 hover:opacity-100 flex items-center justify-center transition-opacity"
                                    >
                                        <X className="h-3 w-3 text-white" />
                                    </button>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="flex-1 h-[1px] bg-border/30" />
                        <span className="text-[10px] uppercase tracking-widest text-muted-foreground opacity-50">Powered by Gemini & Imagen</span>
                    </div>

                    <div className="relative group">
                        <div className="absolute -inset-1 bg-gradient-to-r from-blue-500/30 to-purple-600/30 rounded-2xl opacity-0 group-focus-within:opacity-100 blur-lg transition duration-500" />
                        <div className="relative glass rounded-2xl flex items-center p-2">
                            <input
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="A futuristic cybernetic city in the rain..."
                                className="flex-1 bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground px-4 py-3 text-sm"
                            />
                            <button
                                disabled={isLoading || !prompt.trim()}
                                className={cn(
                                    "h-12 px-6 rounded-xl flex items-center gap-2 transition-all duration-300 font-medium",
                                    prompt.trim() ? "bg-accent text-accent-foreground shadow-lg shadow-accent/20" : "bg-white/5 opacity-50 cursor-not-allowed"
                                )}
                            >
                                {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
                                {isLoading ? "Generating..." : "Generate"}
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
}
