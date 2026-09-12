import { useRef, useEffect } from "react";
import { useApp } from "../../context/AppContext";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import rehypeRaw from "rehype-raw";
import "highlight.js/styles/github.css";
import { FileText } from "lucide-react";

function ChatMessages() {
  const normalizeAssistantContent = (content) => {
  if (typeof content === "string") {
    return content;
  }
  if (Array.isArray(content)) {
    return content
      .map((item) => {
        if (item && typeof item === "object" && item.type === "text") {
          return item.text || "";
        }
        return typeof item === "string" ? item : "";
      })
      .join("\n");
  }
  return String(content ?? "");
};
  const { chatHistory } = useApp();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  if (chatHistory.length === 0) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-center text-4xl font-bold tracking-tight text-white md:text-5xl">
          Hi, how can I help ?
        </p>
      </div>
    );
  }

  return (
    <div className="h-full min-h-0 w-full overflow-y-auto px-4 pb-52 pt-6">
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
        {chatHistory.map((msg, index) => {
          return msg.role === "user" ? (
            <div
              key={index}
              className="flex max-w-[82%] flex-col items-end gap-2 self-end"
            >
              {/* PDF attachment */}
              {msg.attachment && (
                <div className="flex w-[240px] items-center gap-3 rounded-xl border border-slate-700 bg-slate-800 px-3 py-2.5 shadow-sm">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-500/15">
                    <FileText size={17} className="text-indigo-300" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <p className="truncate text-xs font-semibold text-slate-100">
                      {msg.attachment.fileName}
                    </p>

                    <p className="mt-0.5 text-[11px] text-slate-400">PDF</p>
                  </div>
                </div>
              )}

              {/* User message */}
              <div className="rounded-2xl bg-indigo-600 px-4 py-2.5 text-sm leading-6 text-white shadow-sm">
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ) : (
            <div
              key={index}
              className="w-full max-w-3xl self-start px-1 py-2 text-[15px] leading-7 text-slate-300"
            >
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw, rehypeHighlight]}
                components={{
                  h1: ({ children }) => (
                    <h1 className="mb-5 text-2xl font-bold tracking-tight text-white">
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="mb-3 mt-7 text-xl font-semibold tracking-tight text-slate-100">
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="mb-2 mt-5 text-lg font-semibold text-slate-200">
                      {children}
                    </h3>
                  ),
                  p: ({ children }) => (
                    <p className="mb-4 text-[15px] leading-7 text-slate-300">
                      {children}
                    </p>
                  ),
                  ul: ({ children }) => (
                    <ul className="mb-4 list-disc space-y-2 pl-6 text-[15px] leading-7 text-slate-300">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="mb-4 list-decimal space-y-2 pl-6 text-[15px] leading-7 text-slate-300">
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => (
                    <li className="pl-1">
                      {children}
                    </li>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-semibold text-white">
                      {children}
                    </strong>
                  ),
                  em: ({ children }) => (
                    <em className="text-slate-200">
                      {children}
                    </em>
                  ),
                  code: ({ inline, children }) =>
                    inline ? (
                      <code className="rounded-md border border-slate-700 bg-slate-800 px-1.5 py-0.5 font-mono text-[13px] text-indigo-300">
                        {children}
                      </code>
                    ) : (
                      <pre className="my-5 overflow-x-auto rounded-xl border border-slate-700 bg-slate-900 p-4">
                        <code className="font-mono text-[13px] leading-6 text-slate-200">
                          {children}
                        </code>
                      </pre>
                    ),
                  blockquote: ({ children }) => (
                    <blockquote className="my-5 border-l-2 border-indigo-500 pl-4 text-slate-400">
                      {children}
                    </blockquote>
                  ),
                  hr: () => (
                    <hr className="my-6 border-slate-800" />
                  ),
                  table: ({ children }) => (
                    <div className="my-6 overflow-x-auto rounded-xl border border-slate-800">
                      <table className="w-full border-collapse text-sm">
                        {children}
                      </table>
                    </div>
                  ),
                  th: ({ children }) => (
                    <th className="border-b border-slate-700 bg-slate-900/80 px-4 py-3 text-left font-semibold text-slate-100">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="border-b border-slate-800 px-4 py-3 align-top text-[14px] leading-6 text-slate-300">
                      {children}
                    </td>
                  ),
                }}
              >
                {normalizeAssistantContent(msg.content)}
              </ReactMarkdown>
            </div>
          );
        })}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default ChatMessages;