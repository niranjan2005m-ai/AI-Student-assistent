import { LayoutDashboard, Library, Settings, BrainCircuit } from "lucide-react";

function Sidebar() {
  return (
    <div className="flex h-full w-64 flex-col border-r border-slate-800 bg-slate-900 text-slate-300">
      {/* Logo Area */}
      <div className="flex items-center gap-3 border-b border-slate-800 p-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-lg">
          <BrainCircuit size={24} />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-wide text-white">AI PDF</h1>
          <p className="text-xs text-slate-400">Study Assistant</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 p-4">
        {/* Active Item */}
        <a 
          href="#" 
          className="flex items-center gap-3 rounded-xl bg-indigo-600 px-4 py-3 text-white transition-colors"
        >
          <LayoutDashboard size={20} />
          <span className="font-medium">Dashboard</span>
        </a>
        
        {/* Inactive Item */}
        <a 
          href="#" 
          className="flex items-center gap-3 rounded-xl px-4 py-3 transition-colors hover:bg-slate-800 hover:text-white"
        >
          <Library size={20} />
          <span className="font-medium">My Library</span>
        </a>
      </nav>

      {/* Bottom Settings */}
      <div className="border-t border-slate-800 p-4">
        <a 
          href="#" 
          className="flex items-center gap-3 rounded-xl px-4 py-3 transition-colors hover:bg-slate-800 hover:text-white"
        >
          <Settings size={20} />
          <span className="font-medium">Settings</span>
        </a>
      </div>
    </div>
  );
}

export default Sidebar;