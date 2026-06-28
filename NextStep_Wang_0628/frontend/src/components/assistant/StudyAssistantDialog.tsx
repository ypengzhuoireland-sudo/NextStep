import { FormEvent, useState } from "react";
import {
  Bot,
  Loader2,
  MessageSquareText,
  Send,
  Sparkles,
  X
} from "lucide-react";
import {
  chatWithStudyAssistant,
  type AssistantChatResult
} from "@/api/studyAssistant";
import { Button } from "@/components/ui/button";

interface StudyAssistantDialogProps {
  currentExerciseId: string;
  disabled?: boolean;
  onStartExercise: (exerciseId: string) => Promise<void>;
}

interface ChatMessage {
  id: string;
  role: "assistant" | "student";
  text: string;
}

const INITIAL_MESSAGE: ChatMessage = {
  id: "assistant-welcome",
  role: "assistant",
  text: "Tell me what topic or difficulty you want to practise."
};

export function StudyAssistantDialog({
  currentExerciseId,
  disabled = false,
  onStartExercise
}: StudyAssistantDialogProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    INITIAL_MESSAGE
  ]);
  const [recommendation, setRecommendation] =
    useState<AssistantChatResult | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState("");

  /** Send one practice request to the authenticated backend assistant. */
  async function handleSend(event: FormEvent) {
    event.preventDefault();
    const message = input.trim();

    if (!message || isSending) {
      return;
    }

    setMessages((items) => [
      ...items,
      {
        id: `student-${Date.now()}`,
        role: "student",
        text: message
      }
    ]);
    setInput("");
    setError("");
    setIsSending(true);

    try {
      const result = await chatWithStudyAssistant(
        message,
        currentExerciseId
      );
      setMessages((items) => [
        ...items,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          text: result.reason
        }
      ]);
      setRecommendation(result);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "The AI assistant could not respond. Please try again."
      );
    } finally {
      setIsSending(false);
    }
  }

  /** Open the recommended exercise through the existing practice flow. */
  async function handleStartExercise() {
    const exercise = recommendation?.exercise;

    if (!exercise) {
      return;
    }

    setIsStarting(true);
    setError("");
    try {
      await onStartExercise(exercise.id);
      setMessages((items) => [
        ...items,
        {
          id: `assistant-started-${Date.now()}`,
          role: "assistant",
          text: `Opened ${exercise.title}.`
        }
      ]);
      setRecommendation(null);
      setIsOpen(false);
    } catch {
      setError("The exercise could not be opened. Please try again.");
    } finally {
      setIsStarting(false);
    }
  }

  return (
    <>
      <Button
        type="button"
        size="icon"
        className="fixed bottom-5 right-5 z-40 h-12 w-12 rounded-full shadow-2xl"
        onClick={() => setIsOpen((value) => !value)}
        aria-label={isOpen ? "Close AI Study Assistant" : "Open AI Study Assistant"}
      >
        {isOpen ? <X className="h-5 w-5" /> : <MessageSquareText className="h-5 w-5" />}
      </Button>

      {isOpen ? (
        <section
          role="dialog"
          aria-label="AI Study Assistant"
          className="glass-panel fixed bottom-20 right-5 z-40 flex h-[min(520px,calc(100vh-7rem))] w-[min(420px,calc(100vw-2rem))] flex-col overflow-hidden rounded-lg border border-cyan-200/20 shadow-2xl"
        >
          <header className="flex items-center justify-between border-b border-white/10 px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="grid h-9 w-9 place-items-center rounded-lg bg-cyan-300/10 text-cyan-100">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-white">
                  AI Study Assistant
                </h2>
                <p className="mt-0.5 text-xs text-slate-500">
                  AI-powered practice recommender
                </p>
              </div>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
              aria-label="Close AI Study Assistant"
            >
              <X className="h-4 w-4" />
            </Button>
          </header>

          <div className="flex-1 space-y-3 overflow-y-auto p-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={
                  message.role === "student"
                    ? "ml-auto max-w-[85%] rounded-lg bg-primary px-3 py-2 text-sm leading-6 text-white"
                    : "max-w-[88%] rounded-lg border border-white/10 bg-white/[0.05] px-3 py-2 text-sm leading-6 text-slate-200"
                }
              >
                {message.text}
              </div>
            ))}

            {isSending ? (
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                Finding an exercise
              </div>
            ) : null}

            {recommendation?.exercise ? (
              <div className="rounded-lg border border-violet-300/20 bg-violet-300/[0.06] p-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 text-xs text-violet-200">
                      <Sparkles className="h-3.5 w-3.5" />
                      Recommended exercise
                    </div>
                    <h3 className="mt-2 text-sm font-semibold text-white">
                      {recommendation.exercise.title}
                    </h3>
                    <p className="mt-1 text-xs text-slate-400">
                      {recommendation.exercise.primaryKc} ·{" "}
                      {recommendation.exercise.difficulty} ·{" "}
                      {recommendation.exercise.estimatedMinutes} min
                    </p>
                  </div>
                </div>
                <Button
                  type="button"
                  className="mt-3 w-full"
                  onClick={() => void handleStartExercise()}
                  disabled={disabled || isStarting}
                >
                  {isStarting ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Sparkles className="h-4 w-4" />
                  )}
                  Start Exercise
                </Button>
              </div>
            ) : null}

            {error ? (
              <p className="rounded-lg border border-rose-300/20 bg-rose-300/[0.07] px-3 py-2 text-xs text-rose-100">
                {error}
              </p>
            ) : null}
          </div>

          <form
            className="border-t border-white/10 p-3"
            onSubmit={handleSend}
          >
            <div className="flex gap-2">
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Try: an easy loops exercise"
                className="h-10 min-w-0 flex-1 rounded-lg border border-white/10 bg-slate-950/50 px-3 text-sm text-white outline-none placeholder:text-slate-600 focus:border-cyan-300/40 focus:ring-2 focus:ring-cyan-300/10"
                disabled={isSending}
                aria-label="Practice request"
              />
              <Button
                type="submit"
                size="icon"
                disabled={
                  !input.trim() ||
                  isSending
                }
                aria-label="Send practice request"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </form>
        </section>
      ) : null}
    </>
  );
}
