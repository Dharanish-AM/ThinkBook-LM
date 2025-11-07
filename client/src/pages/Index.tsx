import { useState, useEffect } from "react";
import { ThemeToggle } from "@/components/ThemeToggle";
import { UploadPanel, UploadedFile, FileStatus } from "@/components/UploadPanel";
import { ChatPanel, Message } from "@/components/ChatPanel";
import { CitationPanel, Citation } from "@/components/CitationPanel";
import { BookOpen } from "lucide-react";
import { toast } from "sonner";

const Index = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
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
      const res = await fetch("http://localhost:8000/api/upload_file", {
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
          f.id === newFile.id
            ? { ...f, status: "error", progress: 0 }
            : f
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
      const res = await fetch("http://localhost:8000/api/query", {
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
        citations: data.sources?.map(
          (s: any) => `${s.source}::chunk${s.chunk_index}`
        ),
      };

      // Load citation panel data
      const newCitations: Citation[] = data.sources?.map((s: any, i: number) => ({
        id: `cite-${Date.now()}-${i}`,
        docName: s.source.split(".")[0],
        chunkId: `chunk${s.chunk_index}`,
        content: data.raw_retrieval?.[i] || "",
      })) || [];

      setCitations((prev) => [...prev, ...newCitations]);
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
        const res = await fetch("http://localhost:8000/api/list_files");
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

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/30 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
              <BookOpen className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold">ThinkBook LM</h1>
              <p className="text-xs text-muted-foreground">
                Private Document Intelligence Assistant
              </p>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </header>

      {/* Privacy Banner */}
      <div className="bg-success/10 border-y border-success/20 backdrop-blur-sm">
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
      <main className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-8 lg:gap-10 py-2 h-[calc(100vh-200px)] transition-all duration-300 ease-in-out">
          {/* Upload Panel */}
          <aside className="h-full">
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
              disabled={files.length === 0 || !files.some((f) => f.status === "success")}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Citation Panel */}
        {citations.length > 0 && (
          <div className="mt-6 mb-12 min-h-64 max-h-96">
            <CitationPanel
              citations={citations}
              selectedCitation={selectedCitation}
              onSelectCitation={setSelectedCitation}
              onCloseCitation={() => setSelectedCitation(null)}
            />
          </div>
        )}
      </main>
    </div>
  );
};

export default Index;
