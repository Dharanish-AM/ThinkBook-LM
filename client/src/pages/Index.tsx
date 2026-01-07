import { useState, useEffect } from "react";
import { ThemeToggle } from "@/components/ThemeToggle";
import {
  UploadPanel,
  UploadedFile,
  FileStatus,
} from "@/components/UploadPanel";
import { ChatPanel, Message } from "@/components/ChatPanel";
import { BookOpen } from "lucide-react";
import { toast } from "sonner";
import { API_ENDPOINTS } from "@/config/api";

const Index = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Mock data for demo
  const totalDocs = files.filter((f) => f.status === "success").length;
  const totalChunks = files
    .filter((f) => f.status === "success")
    .reduce((sum, f) => sum + (f.chunks || 0), 0);

  const handleFileUpload = async (fileList: FileList) => {
    const file = fileList[0];
    const newFile: UploadedFile = {
      id: `file-${Date.now()}-${Math.random()}`,
      name: file.name,
      status: "processing" as FileStatus,
      progress: 0,
    };
    setFiles((prev) => [...prev, newFile]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(API_ENDPOINTS.uploadFile, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Upload failed");
      }

      const data = await res.json();

      setFiles((prev) =>
        prev.map((f) =>
          f.id === newFile.id
            ? {
                ...f,
                status: "success",
                progress: 100,
                chunks: data.chunks,
              }
            : f
        )
      );

      toast.success(`${file.name} indexed successfully ✓`);
    } catch (err) {
      setFiles((prev) =>
        prev.map((f) =>
          f.id === newFile.id ? { ...f, status: "error", progress: 0 } : f
        )
      );
      toast.error(`Failed to upload ${file.name}`);
    }
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: "user",
      content,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    const formData = new FormData();
    formData.append("q", content);
    formData.append("k", "4");

    try {
      const res = await fetch(API_ENDPOINTS.query, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Query failed");
      }

      const data = await res.json();

      const assistantMessage: Message = {
        id: `msg-${Date.now()}-assistant`,
        role: "assistant",
        content: data.answer,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      toast.error("Error querying documents");
    } finally {
      setIsLoading(false);
    }
  };

  // Load previously indexed files from backend on mount
  useEffect(() => {
    const loadExistingFiles = async () => {
      try {
        const res = await fetch(API_ENDPOINTS.listFiles);
        if (!res.ok) return;
        const data = await res.json(); // expected [{name, chunks}]
        const dbFiles: UploadedFile[] = data.map((f: any) => ({
          id: `db-${f.name}`,
          name: f.name,
          status: "success" as FileStatus,
          progress: 100,
          chunks: f.chunks,
        }));
        setFiles(dbFiles);
      } catch (err) {
        console.error("Failed to load existing files", err);
      }
    };

    loadExistingFiles();
  }, []);

  // Load chat history from local storage
  useEffect(() => {
    const savedMessages = localStorage.getItem("chat_history");

    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error("Failed to parse chat history");
      }
    }
  }, []);

  // Save chat history when messages change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem("chat_history", JSON.stringify(messages));
    }
  }, [messages]);

  const handleClearChat = () => {
    setMessages([]);
    localStorage.removeItem("chat_history");
    toast.info("Chat history cleared");
  };

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      {/* Header */}
      <header className="border-b border-white/5 bg-background/60 backdrop-blur-xl z-50 supports-[backdrop-filter]:bg-background/60 flex-none">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary flex items-center justify-center ring-1 ring-white/10">
              <BookOpen className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
                ThinkBook LM
              </h1>
              <p className="text-xs text-muted-foreground font-medium">
                Private Document Intelligence
              </p>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* Privacy Banner */}
      <div className="bg-success/10 border-y border-success/20 backdrop-blur-sm flex-none">
        <div className="container mx-auto px-6 py-2">
          <p className="text-sm text-center">
            <span className="inline-flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-success animate-pulse" />
              <span className="font-medium">Running locally</span>
              <span className="text-muted-foreground">
                — your data never leaves your device
              </span>
            </span>
          </p>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-6 py-4 overflow-hidden min-h-0">
        <div className="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6 h-full transition-all duration-300 ease-in-out">
          {/* Upload Panel */}
          <aside className="h-full overflow-hidden">
            <UploadPanel
              files={files}
              onFileUpload={handleFileUpload}
              totalDocs={totalDocs}
              totalChunks={totalChunks}
            />
          </aside>

          {/* Chat Panel */}
          <div className="h-full bg-card/30 border border-border/40 rounded-xl p-4 shadow-sm backdrop-blur-sm overflow-hidden">
            <ChatPanel
              messages={messages}
              onSendMessage={handleSendMessage}
              onClearChat={handleClearChat}
              disabled={
                files.length === 0 || !files.some((f) => f.status === "success")
              }
              isLoading={isLoading}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-6 py-2 flex-none" />
    </div>
  );
};

export default Index;
