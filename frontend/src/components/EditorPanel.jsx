import Editor from "@monaco-editor/react";

export default function EditorPanel({ code, setCode }) {
  return (
    <div className="h-full bg-panel rounded-2xl shadow-lg p-2">
      <Editor
        height="70vh"
        defaultLanguage="python"
        theme="vs-dark"
        value={code}
        onChange={(value) => setCode(value)}
      />
    </div>
  );
}
