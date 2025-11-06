import { Card } from "@/components/ui/card";
import { FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface Citation {
  id: string;
  docName: string;
  chunkId: string;
  content: string;
}

interface CitationPanelProps {
  citations: Citation[];
  selectedCitation: Citation | null;
  onSelectCitation: (citation: Citation) => void;
  onCloseCitation: () => void;
}

export function CitationPanel({
  citations,
  selectedCitation,
  onSelectCitation,
  onCloseCitation,
}: CitationPanelProps) {
  return (
    <Card className="glass-panel p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold flex items-center gap-2">
          <FileText className="h-4 w-4" />
          Citations
        </h3>
        {selectedCitation && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onCloseCitation}
            className="h-8 w-8 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {citations.length === 0 ? (
        <p className="text-sm text-muted-foreground text-center py-8">
          Citations will appear here when you ask questions
        </p>
      ) : (
        <div className="space-y-3 overflow-y-auto flex-1 min-h-0">
          {/* Citation Chips */}
          {!selectedCitation && (
            <div className="flex flex-wrap gap-2">
              {citations.map((citation) => (
                <button
                  key={citation.id}
                  onClick={() => onSelectCitation(citation)}
                  className="citation-badge"
                >
                  {citation.docName}::{citation.chunkId}
                </button>
              ))}
            </div>
          )}

          {/* Selected Citation Detail */}
          {selectedCitation && (
            <Card className="p-4 bg-accent/20 border-accent animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="text-sm font-medium font-mono">
                    {selectedCitation.docName}::{selectedCitation.chunkId}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Evidence from document
                  </p>
                </div>
              </div>
              <div className="p-3 bg-background/50 rounded-md border border-border/50 max-h-64 overflow-y-auto">
                <p className="text-sm overflow-y font-mono leading-relaxed whitespace-pre-wrap">
                  {selectedCitation.content}
                </p>
              </div>
            </Card>
          )}
        </div>
      )}
    </Card>
  );
}
