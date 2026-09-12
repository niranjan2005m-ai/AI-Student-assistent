import Sidebar from "../components/Sidebar";
import Header from "../components/Header";

function DashboardLayout({ children }) {
  return (
    <div className="flex h-screen">
      <Sidebar />

      <div className="flex flex-col flex-1">
        <Header />

        <main className="flex-1 overflow-auto bg-gradient-to-br from-slate-50 via-white to-indigo-50">
          {children}
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;