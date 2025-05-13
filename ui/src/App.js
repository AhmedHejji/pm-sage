// src/App.js
import React, { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function App() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const apiUrl = process.env.REACT_APP_API_URL;

  const sendQuery = async () => {
    if (!query.trim()) return;
    try {
      const resp = await axios.post(
        "/generate",
        { query },
        { baseURL: apiUrl }
      );
      setAnswer(resp.data.answer || "No response");
    } catch (err) {
      setAnswer("Error: " + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>PM-Sage Assistant</h1>
      <textarea
        rows={4}
        style={{ width: "100%", padding: "0.5rem" }}
        placeholder="Type your question…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button
        onClick={sendQuery}
        style={{
          marginTop: "0.5rem",
          padding: "0.5rem 1rem",
          backgroundColor: "#007bff",
          color: "#fff",
          border: "none",
          cursor: "pointer"
        }}
      >
        Ask
      </button>

      {/* ANSWER SECTION */}
      <div style={{ marginTop: "1rem" }}>
        <strong>Answer:</strong>
        {answer ? (
          // Only render ReactMarkdown when there is content
          <div style={{ marginTop: "0.5rem", padding: "1rem", background: "#f9f9f9", borderRadius: "4px" }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {answer}
            </ReactMarkdown>
          </div>
        ) : (
          // Show a placeholder if no answer yet
          <p style={{ fontStyle: "italic", color: "#666" }}>Your answer will appear here.</p>
        )}
      </div>
    </div>
  );
}
