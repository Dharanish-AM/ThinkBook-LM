import { Upload, File, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useState } from "react";

export type FileStatus = "pending" | "processing" | "success" | "error";

export interface UploadedFile {
  id: string;
  name: string;
  status: FileStatus;
  chunks?: number;
  progress?: number;
}

interface UploadPanelProps {
  files: UploadedFile[];
  onFileUpload: (files: FileList) => void;
  totalDocs: number;
  totalChunks: number;
}

export function UploadPanel({ files, onFileUpload, totalDocs, totalChunks }: UploadPanelProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files) {
      onFileUpload(e.dataTransfer.files);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      onFileUpload(e.target.files);
    }
  };

  const getStatusIcon = (status: FileStatus) => {
    switch (status) {
      case "success":
        return <CheckCircle2 className="h-4 w-4" />;
      case "error":
        return <AlertCircle className="h-4 w-4" />;
      case "processing":
        return <Loader2 className="h-4 w-4 animate-spin" />;
      default:
        return <File className="h-4 w-4" />;
    }
  };

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Drop Zone */}
      <Card
        className={`glass-card p-8 border-2 border-dashed transition-all ${
          isDragging
            ? "border-primary bg-primary/5 scale-[1.02]"
            : "border-border/50 hover:border-primary/50"
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="flex flex-col items-center justify-center gap-4 text-center">
          <div className={`rounded-full p-4 ${isDragging ? "bg-primary/10" : "bg-muted"}`}>
            <Upload className={`h-8 w-8 ${isDragging ? "text-primary" : "text-muted-foreground"}`} />
          </div>
          <div>
            <p className="font-medium mb-1">
              {isDragging ? "Drop files here" : "Drag & drop files"}
            </p>
            <p className="text-sm text-muted-foreground">PDF, DOCX, or TXT files</p>
          </div>
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,.docx,.txt"
            multiple
            onChange={handleFileInput}
          />
          <Button asChild>
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="h-4 w-4 mr-2" />
              Choose Files
            </label>
          </Button>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3">
        <Card className="glass-panel p-4">
          <p className="text-sm text-muted-foreground mb-1">Documents</p>
          <p className="text-2xl font-bold text-primary">{totalDocs}</p>
        </Card>
        <Card className="glass-panel p-4">
          <p className="text-sm text-muted-foreground mb-1">Chunks</p>
          <p className="text-2xl font-bold text-primary">{totalChunks}</p>
        </Card>
      </div>

      {/* File List */}
      <Card className="glass-panel flex-1 p-4 overflow-hidden">
        <h3 className="font-semibold mb-3">Uploaded Files</h3>
        <div className="space-y-2 overflow-y-auto max-h-[calc(100%-2rem)]">
          {files.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No files uploaded yet
            </p>
          ) : (
            files.map((file) => (
              <Card key={file.id} className="p-3 bg-background/50">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-2 flex-1 min-w-0">
                    <div className={`mt-0.5 ${
                      file.status === "success" ? "text-success" :
                      file.status === "error" ? "text-destructive" :
                      file.status === "processing" ? "text-warning" :
                      "text-muted-foreground"
                    }`}>
                      {getStatusIcon(file.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{file.name}</p>
                      {file.chunks !== undefined && (
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {file.chunks} chunks
                        </p>
                      )}
                    </div>
                  </div>
                  <span className={`status-badge status-${file.status} whitespace-nowrap`}>
                    {file.status === "processing" ? "Processing..." : file.status}
                  </span>
                </div>
                {file.progress !== undefined && file.status === "processing" && (
                  <div className="mt-2 w-full bg-muted rounded-full h-1 overflow-hidden">
                    <div
                      className="h-full bg-primary transition-all duration-300"
                      style={{ width: `${file.progress}%` }}
                    />
                  </div>
                )}
              </Card>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}
