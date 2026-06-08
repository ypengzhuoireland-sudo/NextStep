import { AnimatePresence, motion } from "framer-motion";
import { Bot, Lightbulb, Loader2, MessageSquareText, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { HintMessage } from "@/types/tutor";

interface HintPanelProps {
  messages: HintMessage[];
  isHinting: boolean;
  onRequestHint: (level: 1 | 2 | 3) => void;
}

export function HintPanel({ messages, isHinting, onRequestHint }: HintPanelProps) {
  const nextLevel = Math.min(messages.length + 1, 3) as 1 | 2 | 3;

  return (
    <Card>
      <CardHeader className="border-b border-white/10">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-4 w-4 text-cyan-200" />
            AI Hint
          </CardTitle>
          <p className="mt-1 text-xs text-slate-500">Layered guidance based on latest attempt</p>
        </div>
        <Badge variant="violet">
          <Sparkles className="h-3.5 w-3.5" />
          adaptive
        </Badge>
      </CardHeader>

      <CardContent className="space-y-4 p-4">
        <div className="max-h-[330px] space-y-3 overflow-auto pr-1">
          <AnimatePresence initial={false}>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 12, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8 }}
                className="flex gap-3"
              >
                <div className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-cyan-300/20 to-violet-300/20 ring-1 ring-white/10">
                  <MessageSquareText className="h-4 w-4 text-cyan-100" />
                </div>
                <div className="min-w-0 flex-1 rounded-lg rounded-tl-sm border border-white/10 bg-white/[0.055] p-3">
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-sm font-medium text-white">{message.title}</div>
                    <div className="text-[10px] text-slate-500">{message.createdAt}</div>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-slate-300">{message.text}</p>
                  <div className="mt-3 flex items-center gap-2 text-[11px] text-slate-500">
                    <span>level {message.level}</span>
                    <span className="h-1 w-1 rounded-full bg-slate-600" />
                    <span>{message.kcCode}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        <div className="grid grid-cols-3 gap-2">
          {[1, 2, 3].map((level) => (
            <Button
              key={level}
              variant={level === nextLevel ? "default" : "secondary"}
              size="sm"
              disabled={isHinting}
              onClick={() => onRequestHint(level as 1 | 2 | 3)}
            >
              {isHinting && level === nextLevel ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Lightbulb className="h-3.5 w-3.5" />
              )}
              L{level}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
