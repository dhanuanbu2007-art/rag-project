import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hi! 👋 I'm your study-material assistant. Ask me anything about the uploaded documents.",
      sources: [],
    },
  ]);

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!question.trim() || loading) return;

    const userMessage = question.trim();

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: userMessage,
        sources: [],
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userMessage,
        }),
      });

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "Sorry, I couldn't connect to the backend.",
          sources: [],
        },
      ]);
    }

    setLoading(false);
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="app">

      <header className="header">
        <div className="brand">
          <div className="logo">📚</div>

          <div>
            <h1>Study Assistant</h1>
            <p>Multi-Document RAG</p>
          </div>
        </div>

        <div className="status">
          <span></span>
          Online
        </div>
      </header>


      <main className="chat-area">

        <div className="welcome">
          <div className="bot-icon">🤖</div>

          <h2>Ask your study materials</h2>

          <p>
            Ask questions from your uploaded documents
            and get answers with sources.
          </p>
        </div>


        <div className="messages">

          {messages.map((message, index) => (

            <div
              key={index}
              className={`message-row ${message.role}`}
            >

              <div className="avatar">
                {message.role === "assistant" ? "🤖" : "👤"}
              </div>

              <div className="message-content">

                <div className="message-name">
                  {message.role === "assistant"
                    ? "Assistant"
                    : "You"}
                </div>

                <div className="message-bubble">
                       <ReactMarkdown>{message.text}</ReactMarkdown>
</div>


                {message.sources.length > 0 && (
                  <div className="sources">

                    <div className="sources-title">
                      📚 Sources
                    </div>

                    <div className="source-list">

                      {message.sources.map(
                        (source, sourceIndex) => (
                          <span
                            className="source"
                            key={sourceIndex}
                          >
                            📄 {source}
                          </span>
                        )
                      )}

                    </div>

                  </div>
                )}

              </div>

            </div>

          ))}


          {loading && (

            <div className="message-row assistant">

              <div className="avatar">🤖</div>

              <div className="message-content">

                <div className="message-name">
                  Assistant
                </div>

                <div className="message-bubble typing">
                  Thinking...
                </div>

              </div>

            </div>

          )}

        </div>

      </main>


      <footer className="input-area">

        <div className="input-box">

          <input
            type="text"
            placeholder="Ask something about your study materials..."
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={handleKeyDown}
            disabled={loading}
          />

          <button
            onClick={sendMessage}
            disabled={loading || !question.trim()}
          >
            ➤
          </button>

        </div>

        <p className="footer-note">
          Answers are generated from the uploaded study materials.
        </p>

      </footer>

    </div>
  );
}

export default App;