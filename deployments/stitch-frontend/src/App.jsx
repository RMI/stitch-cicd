import ResourcesView from "./components/ResourcesView";
import ResourceView from "./components/ResourceView";

function App() {

  return (
    <div className="min-h-screen w-screen bg-gray-100 p-8">
      <ResourcesView endpoint="/api/v1/resources" />
      <ResourceView className="mt-24" endpoint="/api/v1/resources/{id}" />
    </div>
  );
}

export default App;

