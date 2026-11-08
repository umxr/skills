import { createRoot } from "react-dom/client";
import { Button } from "@harbor/ui";
import { createClient } from "@harbor/api-client";

const api = createClient(import.meta.env.VITE_API_URL);

function App() {
  return <Button onClick={() => api.listShipments().then(console.log)}>Load</Button>;
}

createRoot(document.getElementById("root")!).render(<App />);
