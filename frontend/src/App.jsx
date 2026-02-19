import { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import { useRef } from "react";

function App() {
  const [prompt, setPrompt] = useState("");
  const [code, setCode] = useState("");
  const [output, setOutput] = useState("");
  const socketRef = useRef(null);
  const [stdin, setStdin] = useState("");



  // ✅ WebSocket Setup
useEffect(() => {
  const ws = new WebSocket("ws://127.0.0.1:8000/ws");

  ws.onopen = () => {
    console.log("WebSocket connected");
  };

  ws.onmessage = (event) => {
    setOutput(prev => prev + event.data);
  };

  ws.onclose = () => {
    console.log("WebSocket closed");
  };

  socketRef.current = ws;

  return () => ws.close();
}, []);


  // ✅ Generate Code (ONLY generate)
  const handleGenerate = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/generate", {
        prompt,
      });

      setCode(response.data.code);
      setOutput("");
    } catch (error) {
      console.error(error);
    }
  };

  // ✅ Run Code (start process ONCE)
  const handleRun = () => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN){
      alert("WebSocket not connected");
      return;
    }

    setOutput("");

    socketRef.current.send(
      JSON.stringify({
        type: "run",   // 🔥 must match backend
        code: code,
      })
    );
  };

  // ✅ Send input when Enter pressed
  const handleInputKey = (e) => {
  if (e.key === "Enter") {
    e.preventDefault();

    if (
      !socketRef.current ||
      socketRef.current.readyState !== WebSocket.OPEN
    ) {
      alert("WebSocket not connected");
      return;
    }

    socketRef.current.send(
      JSON.stringify({
        type: "input",
        input: e.target.value,  // ⚠ must match backend
      })
    );

    e.target.value = "";
  }
};


  // ✅ Debug Code
  const handleDebug = async () => {
  try {
    const response = await axios.post("http://127.0.0.1:8000/debug", {
      code: code,
      stdin: ""   // simple fix — no dependency
    });

    setOutput(response.data.output);

    if (response.data.fixed_code && response.data.fixed_code !== code) {
      setCode(response.data.fixed_code);
      alert("Code auto-corrected ✔");
    } else {
      setOutput(prev => prev + "\nNo fixes suggested.");
    }

  } catch (error) {
    console.error("Debug error:", error);
  }
};




  return (
    <div style={{ background: "#0b1a2b", minHeight: "100vh", color: "white", padding: "20px" }}>
      <h1 style={{ fontSize: "32px", marginBottom: "20px" }}>
        AI Autonomous IDE
      </h1>

      {/* Prompt */}
      <div style={{ display: "flex", marginBottom: "20px" }}>
        <input
          type="text"
          placeholder="Enter prompt to generate Python code..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          style={{
            flex: 1,
            padding: "10px",
            fontSize: "16px",
            background: "#1e293b",
            color: "white",
            border: "1px solid #333",
          }}
        />
        <button
          type="button"
          onClick={handleGenerate}
          style={{
            padding: "10px 20px",
            marginLeft: "10px",
            background: "#2563eb",
            color: "white",
            border: "none",
            cursor: "pointer",
          }}
        >
          Generate
        </button>
      </div>

      <div style={{ display: "flex", gap: "20px" }}>
        {/* Code Editor */}
        <div style={{ flex: 1 }}>
          <h2>Code Editor</h2>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            style={{
              width: "100%",
              height: "300px",
              background: "#111827",
              color: "#00ff88",
              fontFamily: "monospace",
              fontSize: "14px",
              padding: "10px",
              border: "1px solid #333",
            }}
          />

          {/* Program Input */}
          <h3 style={{ marginTop: "15px" }}>Program Input (Press Enter)</h3>
          <input
            type="text"
            placeholder="Type input and press Enter"
            onKeyDown={handleInputKey}
            style={{
              width: "100%",
              height: "40px",
              background: "#111827",
              color: "white",
              padding: "10px",
              border: "1px solid #333",
              marginBottom: "10px",
            }}
          />

          <div>
            <button
              type="button"
              onClick={handleDebug}
              style={{
                padding: "8px 16px",
                marginRight: "10px",
                background: "#f59e0b",
                border: "none",
                cursor: "pointer",
              }}
            >
              Debug
            </button>

            <button
              type="button"
              onClick={handleRun}
              style={{
                padding: "8px 16px",
                background: "#22c55e",
                border: "none",
                cursor: "pointer",
              }}
            >
              Run
            </button>
          </div>
        </div>

        {/* Output */}
        <div style={{ flex: 1 }}>
          <h2>Output</h2>
          <textarea
            value={output}
            readOnly
            style={{
              width: "100%",
              height: "400px",
              background: "#111827",
              color: "white",
              fontFamily: "monospace",
              padding: "10px",
              border: "1px solid #333",
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
