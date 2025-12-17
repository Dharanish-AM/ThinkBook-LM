import { Send, Bot, User, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: string[];
}

interface ChatPanelProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  onClearChat?: () => void;
  disabled?: boolean;
  isLoading?: boolean;
}

export function ChatPanel({
  messages,
  onSendMessage,
  onClearChat,
  disabled,
  isLoading,
}: ChatPanelProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = () => {
    if (input.trim() && !disabled && !isLoading) {
      onSendMessage(input.trim());
      setInput("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const MarkdownComponents = {
    // Style other elements to match Shadcn/Tailwind aesthetics
    ul: ({ children }: any) => (
      <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>
    ),
    ol: ({ children }: any) => (
      <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>
    ),
    h1: ({ children }: any) => (
      <h1 className="text-xl font-bold mb-2 mt-4">{children}</h1>
    ),
    h2: ({ children }: any) => (
      <h2 className="text-lg font-semibold mb-2 mt-3">{children}</h2>
    ),
    h3: ({ children }: any) => (
      <h3 className="text-md font-semibold mb-1 mt-2">{children}</h3>
    ),
    p: ({ children }: any) => (
      <p className="leading-relaxed mb-2 last:mb-0">{children}</p>
    ),
    blockquote: ({ children }: any) => (
      <blockquote className="border-l-4 border-primary/30 pl-4 py-1 my-4 italic text-muted-foreground bg-muted/30 rounded-r-md">
        {children}
      </blockquote>
    ),
    table: ({ children }: any) => (
      <div className="my-4 w-full overflow-y-auto rounded-lg border border-border/50">
        <table className="w-full text-sm">{children}</table>
      </div>
    ),
    thead: ({ children }: any) => (
      <thead className="bg-muted/50 text-left font-medium">{children}</thead>
    ),
    tbody: ({ children }: any) => (
      <tbody className="divide-y divide-border/50 bg-card/50">{children}</tbody>
    ),
    tr: ({ children }: any) => (
      <tr className="transition-colors hover:bg-muted/50">{children}</tr>
    ),
    th: ({ children }: any) => (
      <th className="px-4 py-3 align-middle font-medium text-muted-foreground">
        {children}
      </th>
    ),
    td: ({ children }: any) => (
      <td className="px-4 py-3 align-middle">{children}</td>
    ),
    code: ({ node, inline, className, children, ...props }: any) => {
      return inline ? (
        <code
          className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono text-primary"
          {...props}
        >
          {children}
        </code>
      ) : (
        <pre className="bg-zinc-950 dark:bg-zinc-900 border border-border/50 p-4 rounded-lg overflow-x-auto text-sm font-mono my-4 shadow-sm">
          <code {...props} className="text-zinc-50 dark:text-zinc-50">
            {children}
          </code>
        </pre>
      );
    },
  };

  return (
    <div className="flex flex-col h-full">
      {/* Model Status */}
      <Card className="glass-panel p-3 mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
          <span className="text-sm font-medium">Llama-3.1-8B (Local)</span>
          <span className="text-xs text-muted-foreground ml-2 hidden sm:inline">
            Your data never leaves your device
          </span>
        </div>
        {messages.length > 0 && onClearChat && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearChat}
            className="h-7 text-xs text-muted-foreground hover:text-destructive"
            title="Clear Chat History"
          >
            <Trash2 className="h-3.5 w-3.5 mr-1" />
            Clear
          </Button>
        )}
      </Card>

      {/* Chat Messages */}
      <Card className="glass-panel flex-1 p-4 overflow-hidden mb-4">
        <div className="h-full overflow-y-auto space-y-4 pr-2">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-4">
              <Bot className="h-12 w-12 text-muted-foreground mb-4 opacity-50" />
              <p className="text-lg font-medium mb-2">Ready to assist</p>
              <p className="text-sm text-muted-foreground max-w-md">
                Upload research material to begin asking questions. I'll provide
                answers with citations from your documents.
              </p>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {message.role === "assistant" && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center mt-1">
                      <Bot className="h-5 w-5 text-primary" />
                    </div>
                  )}
                  <Card
                    className={`max-w-[85%] p-4 shadow-sm ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-card"
                    }`}
                  >
                    <div className="text-sm">
                      {message.role === "assistant" ? (
                        <div className="prose dark:prose-invert max-w-none text-sm break-words">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={MarkdownComponents}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <p className="whitespace-pre-wrap break-words">
                          {message.content}
                        </p>
                      )}
                    </div>
                  </Card>
                  {message.role === "user" && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center mt-1">
                      <User className="h-5 w-5 text-secondary-foreground" />
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <Card className="p-4 bg-card">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" />
                      <div
                        className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      />
                      <div
                        className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      />
                    </div>
                  </Card>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </Card>

      {/* Input */}
      <Card className="glass-panel p-4">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              disabled ? "Upload documents first..." : "Ask a question..."
            }
            disabled={disabled || isLoading}
            className="flex-1"
          />
          <Button
            onClick={handleSend}
            disabled={disabled || isLoading || !input.trim()}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </Card>
    </div>
  );
}
