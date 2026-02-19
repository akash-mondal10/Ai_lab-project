export default function OutputPanel({ output }) {
  return (
    <div className="bg-panel p-4 rounded-2xl mt-4 shadow-lg">
      <h2 className="text-lg font-bold mb-2">Output</h2>
      <pre className="text-green-400 whitespace-pre-wrap">{output}</pre>
    </div>
  );
}
