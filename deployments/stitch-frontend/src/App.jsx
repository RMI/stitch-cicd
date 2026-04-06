import { Routes, Route } from "react-router-dom";
import EnvironmentBanner from "./components/EnvironmentBanner";
import HomePage from "./pages/HomePage";
import ResourceDetailPage from "./pages/ResourceDetailPage";
import { LogoutButton } from "./components/LogoutButton";

function App() {
  return (
    <div className="min-h-screen w-screen bg-white">
      <EnvironmentBanner />
      <div className="p-8">
      <div className="max-w-4xl mx-auto flex justify-end mb-4">
        <LogoutButton />
      </div>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/oil-gas-fields/:id" element={<ResourceDetailPage />} />
      </Routes>
      </div>
    </div>
  );
}

export default App;
