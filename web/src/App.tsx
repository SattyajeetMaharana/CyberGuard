import "./App.css";

import { BrowserRouter } from "react-router-dom";

import AppRoutes from "./routes/AppRoutes";
import StartupTransition from "./components/StartupTransition";

function App() {
  return (
    <BrowserRouter>
      <StartupTransition>
        <AppRoutes />
      </StartupTransition>
    </BrowserRouter>
  );
}

export default App;