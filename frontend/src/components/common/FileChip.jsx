import {
  FileText,
  Loader2,
  CheckCircle2,
  X,
} from "lucide-react";

function FileChip({
  uploadedFile,
  uploadStatus,
  progress,
  onRemove,
}) {
  if (!uploadedFile) return null;

  return (
    <div className="rounded-2xl border border-slate-700 bg-slate-900 p-4 shadow-sm">
      <div className="flex items-center justify-between">

        <div className="flex items-center gap-3">

          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800 text-indigo-400">
            <FileText size={20} />
          </div>

          <div>
            <p className="font-semibold text-slate-200">
              {uploadedFile.name}
            </p>

            <div className="mt-1 flex items-center gap-2 text-xs">

              <span className="text-slate-400">
                {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
              </span>

              <span className="text-slate-600">•</span>

              {uploadStatus === "uploading" && (
                <span className="flex items-center gap-1 text-indigo-400">
                  <Loader2 size={12} className="animate-spin" />
                  Uploading {progress}%
                </span>
              )}

              {uploadStatus === "ready" && (
                <span className="flex items-center gap-1 text-emerald-400">
                  <CheckCircle2 size={12} />
                  Indexed Successfully
                </span>
              )}

              {uploadStatus === "error" && (
                <span className="text-red-400">
                  Upload Failed
                </span>
              )}

            </div>
          </div>
        </div>

        <button
          onClick={onRemove}
          className="rounded-full p-2 text-slate-500 transition hover:bg-red-900/30 hover:text-red-400"
        >
          <X size={18} />
        </button>

      </div>
    </div>
  );
}

export default FileChip;