import { Search, Bell, Settings } from "lucide-react";

function Header() {
  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white/60 px-6 py-4 backdrop-blur-md sticky top-0 z-10">
      {/* Search Bar */}
      <div className="relative w-full max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
        <input
          type="text"
          placeholder="Search documents, chats, or notes..."
          className="w-full rounded-full border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm text-slate-700 outline-none transition-all focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-50"
        />
      </div>

      {/* Right Side Icons & Profile */}
      <div className="flex items-center gap-2 md:gap-4">
        {/* Notification Bell with Ping */}
        <button className="relative rounded-full p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-800">
          <Bell size={20} />
          <span className="absolute right-1.5 top-1.5 h-2.5 w-2.5 rounded-full border-2 border-white bg-red-500"></span>
        </button>
        
        {/* Settings Icon */}
        <button className="rounded-full p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-800">
          <Settings size={20} />
        </button>
        
        {/* User Profile */}
        <div className="ml-2 flex cursor-pointer items-center gap-3 border-l border-slate-200 pl-4 transition-opacity hover:opacity-80">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-sm font-bold text-white shadow-sm">
            N
          </div>
          <span className="hidden text-sm font-medium text-slate-700 md:block">
            Niranjan
          </span>
        </div>
      </div>
    </header>
  );
}

export default Header;