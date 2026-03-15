"use client";

import { useState, useRef, useEffect } from "react";
import { Search, Database, FileText, CheckCircle2, Clock, AlertCircle, Upload, X, Loader2, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface JobInfo {
    document: string;
    job_id: string;
    status: string;
    message?: string;
}

export default function IngestPage() {
    const [files, setFiles] = useState<File[]>([]);
    const [jobs, setJobs] = useState<JobInfo[]>([]);
    const [targetJobId, setTargetJobId] = useState("");
    const [checkedJob, setCheckedJob] = useState<any | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isChecking, setIsChecking] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFiles = Array.from(e.target.files || []);
        const newFiles = [...files, ...selectedFiles].slice(0, 5);
        setFiles(newFiles);
        setError(null);
    };

    const removeFile = (index: number) => {
        setFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleIngest = async () => {
        if (files.length === 0 || isUploading) return;

        setIsUploading(true);
        setError(null);

        try {
            const formData = new FormData();
            files.forEach(f => formData.append("files", f));
            formData.append("overwrite", "true");

            const res = await fetch(`${API_BASE}/kb/ingest`, {
                method: "POST",
                body: formData,
            });

            if (!res.ok) throw new Error("Upload failed");

            const data = await res.json();
            setJobs(prev => [...data.results, ...prev]);
            setFiles([]);
        } catch (err) {
            setError("Failed to initiate ingestion.");
        } finally {
            setIsUploading(false);
        }
    };

    const checkJobStatus = async (id?: string) => {
        const jid = id || targetJobId;
        if (!jid || isChecking) return;

        setIsChecking(true);
        try {
            const res = await fetch(`${API_BASE}/kb/ingest/status/${jid}`);
            if (!res.ok) throw new Error("Job not found");
            const data = await res.json();
            setCheckedJob(data);
        } catch (err) {
            setError("Could not find job status for ID: " + jid);
        } finally {
            setIsChecking(false);
        }
    };

    return (
        <div className="flex flex-col h-full w-full">
            <header className="flex h-16 items-center border-b border-border/50 px-4 lg:px-8 pl-14 lg:pl-8 sticky top-0 bg-background/50 backdrop-blur-md z-10">
                <div className="flex items-center gap-2">
                    <Database className="h-4 w-4 text-accent" />
                    <h1 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Knowledge Base</h1>
                </div>
            </header>

            <div className="flex-1 overflow-y-auto px-4 lg:px-8 py-10">
                <div className="max-w-4xl mx-auto space-y-12 pb-20">

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                        {/* Upload Section */}
                        <section className="space-y-6">
                            <div className="space-y-1">
                                <h3 className="text-lg font-medium">Ingest Documents</h3>
                                <p className="text-xs text-muted-foreground">Add new technical specs or documentation to the vector store.</p>
                            </div>

                            <div
                                onClick={() => fileInputRef.current?.click()}
                                className="border-2 border-dashed border-border/50 rounded-3xl p-10 flex flex-col items-center justify-center gap-4 bg-white/[0.02] hover:bg-white/[0.04] hover:border-accent/40 transition-all cursor-pointer group relative overflow-hidden"
                            >
                                <div className="h-14 w-14 rounded-2xl bg-accent/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                                    <Upload className="h-7 w-7 text-accent" />
                                </div>
                                <div className="text-center z-10">
                                    <p className="text-sm font-medium">Click or drag to select</p>
                                    <p className="text-xs text-muted-foreground mt-1">PDF, CSV, YAML, Markdown</p>
                                </div>
                                <input
                                    type="file"
                                    multiple
                                    className="hidden"
                                    ref={fileInputRef}
                                    onChange={handleFileChange}
                                />
                            </div>

                            <AnimatePresence>
                                {files.length > 0 && (
                                    <motion.div
                                        initial={{ opacity: 0, height: 0 }}
                                        animate={{ opacity: 1, height: "auto" }}
                                        exit={{ opacity: 0, height: 0 }}
                                        className="space-y-2 overflow-hidden"
                                    >
                                        <div className="flex items-center justify-between px-2">
                                            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Queue ({files.length}/5)</span>
                                            <button onClick={() => setFiles([])} className="text-[10px] text-accent hover:underline">Clear All</button>
                                        </div>
                                        {files.map((f, i) => (
                                            <div key={i} className="flex items-center justify-between p-3 rounded-xl glass border-white/5 group">
                                                <div className="flex items-center gap-3 min-w-0">
                                                    <FileText className="h-4 w-4 text-accent/60" />
                                                    <span className="text-xs font-medium truncate">{f.name}</span>
                                                </div>
                                                <button onClick={() => removeFile(i)} className="p-1 hover:bg-white/10 rounded-md transition-colors opacity-0 group-hover:opacity-100">
                                                    <X className="h-3 w-3 text-muted-foreground" />
                                                </button>
                                            </div>
                                        ))}
                                        <button
                                            onClick={handleIngest}
                                            disabled={isUploading}
                                            className="w-full mt-4 py-3 rounded-xl bg-accent text-accent-foreground font-semibold text-sm shadow-lg shadow-accent/20 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2"
                                        >
                                            {isUploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                                            {isUploading ? "Ingesting..." : "Start Ingestion"}
                                        </button>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </section>

                        {/* Status Section */}
                        <section className="space-y-6">
                            <div className="space-y-1">
                                <h3 className="text-lg font-medium">Track Status</h3>
                                <p className="text-xs text-muted-foreground">Monitor the progress of your ingestion workers.</p>
                            </div>

                            <div className="flex gap-2">
                                <input
                                    value={targetJobId}
                                    onChange={(e) => setTargetJobId(e.target.value)}
                                    placeholder="Job ID..."
                                    className="flex-1 glass px-4 py-3 rounded-xl outline-none border-none focus:ring-1 focus:ring-accent/50 transition-all font-mono text-xs"
                                />
                                <button
                                    onClick={() => checkJobStatus()}
                                    disabled={!targetJobId || isChecking}
                                    className="bg-white/5 border border-white/5 px-4 rounded-xl hover:bg-white/10 transition-colors disabled:opacity-50"
                                >
                                    {isChecking ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4 text-muted-foreground" />}
                                </button>
                            </div>

                            <AnimatePresence>
                                {checkedJob && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="p-5 rounded-2xl glass border-accent/20 space-y-4"
                                    >
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">Job Details</span>
                                            <div className={cn(
                                                "px-2 py-0.5 rounded text-[10px] font-bold uppercase",
                                                checkedJob.status === "completed" ? "bg-green-500/10 text-green-400" :
                                                    checkedJob.status === "error" ? "bg-red-500/10 text-red-400" : "bg-accent/10 text-accent"
                                            )}>
                                                {checkedJob.status}
                                            </div>
                                        </div>
                                        <div className="space-y-2">
                                            <div className="flex items-center gap-2">
                                                <FileText className="h-4 w-4 text-muted-foreground" />
                                                <span className="text-sm font-medium truncate">{checkedJob.filename}</span>
                                            </div>
                                            <div className="text-[10px] text-muted-foreground font-mono">
                                                ID: {checkedJob.job_id}
                                            </div>
                                        </div>
                                        {checkedJob.metadata && (
                                            <div className="grid grid-cols-2 gap-4 pt-2">
                                                <div className="space-y-1 text-center p-2 rounded-lg bg-white/5">
                                                    <span className="text-[10px] text-muted-foreground block">Nodes</span>
                                                    <span className="text-sm font-mono">{checkedJob.metadata.nodes_created || 0}</span>
                                                </div>
                                                <div className="space-y-1 text-center p-2 rounded-lg bg-white/5">
                                                    <span className="text-[10px] text-muted-foreground block">Embeddings</span>
                                                    <span className="text-sm font-mono">{checkedJob.metadata.embeddings_stored || 0}</span>
                                                </div>
                                            </div>
                                        )}
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            <div className="space-y-3">
                                <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground px-2">Recent Submissions</h4>
                                {jobs.length === 0 ? (
                                    <div className="p-10 rounded-2xl glass border-dashed border-white/5 flex flex-col items-center text-center opacity-30">
                                        <Clock className="h-6 w-6 mb-2" />
                                        <span className="text-xs">No jobs in current session.</span>
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        {jobs.map((job, i) => (
                                            <div key={job.job_id} className="p-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between group">
                                                <div className="flex flex-col min-w-0">
                                                    <span className="text-xs font-medium truncate max-w-[150px]">{job.document}</span>
                                                    <span className="text-[9px] font-mono text-muted-foreground">{job.job_id.slice(0, 8)}...</span>
                                                </div>
                                                <button
                                                    onClick={() => checkJobStatus(job.job_id)}
                                                    className="p-1.5 rounded-lg bg-accent/10 text-accent opacity-0 group-hover:opacity-100 transition-opacity"
                                                >
                                                    <Search className="h-3 w-3" />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </section>
                    </div>

                    <div className="flex items-center gap-3 p-4 rounded-2xl bg-accent/5 border border-accent/10">
                        <AlertCircle className="h-5 w-5 text-accent shrink-0" />
                        <p className="text-xs text-muted-foreground">
                            Ingestion is asynchronous. Large PDF or CSV files may take several minutes to process and appear in the `search_kb` tool's results.
                        </p>
                    </div>

                </div>
            </div>
        </div>
    );
}
