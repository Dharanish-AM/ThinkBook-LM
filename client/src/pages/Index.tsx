import { useState } from "react";
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

  const handleFileUpload = (fileList: FileList) => {
    const newFiles: UploadedFile[] = Array.from(fileList).map((file) => ({
      id: `file-${Date.now()}-${Math.random()}`,
      name: file.name,
      status: "processing" as FileStatus,
      progress: 0,
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    // Simulate processing
    newFiles.forEach((file, index) => {
      setTimeout(() => {
        // Simulate progress
        const progressInterval = setInterval(() => {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === file.id && f.progress !== undefined && f.progress < 90
                ? { ...f, progress: f.progress + 10 }
                : f
            )
          );
        }, 200);

        // Complete after 2 seconds
        setTimeout(() => {
          clearInterval(progressInterval);
          setFiles((prev) =>
            prev.map((f) =>
              f.id === file.id
                ? {
                    ...f,
                    status: "success" as FileStatus,
                    progress: 100,
                    chunks: Math.floor(Math.random() * 20) + 10,
                  }
                : f
            )
          );
          toast.success(`${file.name} indexed successfully ✓`);
        }, 2000 + index * 500);
      }, index * 200);
    });
  };

  const handleSendMessage = (content: string) => {
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: "user",
      content,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const mockCitations: Citation[] = [
        {
          id: `cite-${Date.now()}-1`,
          docName: files[0]?.name?.split(".")[0] || "document",
          chunkId: "chunk3",
          content:
            "This is the relevant excerpt from the document that supports the answer. It contains detailed information about the topic discussed in the query.",
        },
        {
          id: `cite-${Date.now()}-2`,
          docName: files[1]?.name?.split(".")[0] || "research",
          chunkId: "chunk7",
          content:
            "Additional supporting evidence from another document. This provides context and further validation for the response provided.",
        },
      ];

      const assistantMessage: Message = {
        id: `msg-${Date.now()}-assistant`,
        role: "assistant",
        content: `Based on the documents, here's what I found: The research indicates significant findings in this area [${mockCitations[0].docName}::${mockCitations[0].chunkId}]. This is further supported by evidence from [${mockCitations[1].docName}::${mockCitations[1].chunkId}], which provides additional context and validation.`,
        citations: mockCitations.map((c) => `${c.docName}::${c.chunkId}`),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setCitations((prev) => [...prev, ...mockCitations]);
      setIsLoading(false);
    }, 1500);
  };

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
        <div className="grid lg:grid-cols-[380px_1fr] gap-6 h-[calc(100vh-180px)]">
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
          <div className="h-full">
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
          <div className="mt-6 h-64">
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
