import { Routes, Route, Link } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ResourceDetailPage from "./pages/ResourceDetailPage";
import EntityLinkagePage from "./pages/EntityLinkagePage";
import { LogoutButton } from "./components/LogoutButton";

function App() {
  return (
    <div className="min-h-screen w-screen bg-white p-8">
      <Link to="/">Home</Link>
      <Link to="/entity-linkage">Entity Linkage</Link>
      <div className="max-w-4xl mx-auto flex justify-end mb-4">
        <LogoutButton />
      </div>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/oil-gas-fields/:id" element={<ResourceDetailPage />} />
        <Route path="/entity-linkage" element={<EntityLinkagePage />} />
      </Routes>
    </div>
  );
}

export default App;
