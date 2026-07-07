import React, { useEffect, useRef, useState } from "react";
import { useStadium } from "../hooks/useStadium";
import { Language } from "../lib/types";
import { LanguageSelector } from "./LanguageSelector";

interface Props {
  stadium: ReturnType<typeof useStadium>;
}

export const FanAssistant: React.FC<Props> = ({ stadium }) => {
  const { state, askAssistant, loadHistory } = stadium;
  const [question, setQuestion] = useState("");
  const [language, setLanguage] = useState<Language>("en");
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  useEffect(() => {
    // Scroll to latest message
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [state.history, state.assistantResponse]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || state.loading) return;
    askAssistant(question, language, "concourse_north");
    setQuestion("");
  };

  const handleChipClick = (suggestion: string) => {
    askAssistant(suggestion, language, "concourse_north");
  };

  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>Multilingual Fan Assistant</h2>
        <LanguageSelector value={language} onChange={setLanguage} />
      </div>

      <div className="chat-container">
        <div className="chat-history" role="log" aria-live="polite">
          {state.history.length === 0 && !state.assistantResponse && (
            <div className="chat-message assistant">
              Hello! I am StadiumIQ, your helper for the FIFA World Cup 2026. How can I assist you
              today?
            </div>
          )}

          {state.history
            .slice()
            .reverse()
            .map((msg, i) => (
              <React.Fragment key={msg.id || i}>
                <div className="chat-message user">{msg.question}</div>
                <div className="chat-message assistant">
                  {msg.answer}
                  <span className="source-badge">{msg.source}</span>
                </div>
              </React.Fragment>
            ))}

          {state.loading && (
            <div className="chat-message assistant" style={{ fontStyle: "italic" }}>
              Thinking...
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Suggested actions list */}
        {state.assistantResponse?.suggested_actions && (
          <div className="chat-actions">
            {state.assistantResponse.suggested_actions.map((act, i) => (
              <button
                key={i}
                className="action-chip"
                onClick={() => handleChipClick(act.details)}
                type="button"
              >
                {act.details}
              </button>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit} className="chat-input-area">
          <input
            type="text"
            placeholder="Ask about restrooms, medical help, metro, transit..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={state.loading}
            aria-label="Fan query input"
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={state.loading || !question.trim()}
            aria-busy={state.loading}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};
