import DashboardLayout from "../layouts/DashboardLayout";
import Hero from "../components/Landing/Hero";
import ChatInput from "../components/Landing/ChatInput";
import QuickActions from "../components/Landing/QuickActions";
import RecentDocuments from "../components/Landing/RecentDocuments";

function Home() {
  return (
    <DashboardLayout>
      <div className="relative flex min-h-full flex-col items-center px-8 py-16">
        {/* Glassmorphism Background Blobs */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute left-20 top-20 h-72 w-72 rounded-full bg-indigo-200/30 blur-3xl" />
          <div className="absolute right-20 bottom-20 h-80 w-80 rounded-full bg-violet-200/30 blur-3xl" />
        </div>
        
        <Hero />
        <ChatInput />
        <QuickActions />
        <RecentDocuments />
      </div>
    </DashboardLayout>
  );
}

export default Home;