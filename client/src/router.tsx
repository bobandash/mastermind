import { createBrowserRouter } from "react-router-dom";
import HomePage from "./pages/Home";
import SingleplayerSelect from "./pages/SingleplayerSelect";

const router = createBrowserRouter([
  {
    path: "/",
    element: <HomePage />,
  },
  {
    path: "/singleplayer-select",
    element: <SingleplayerSelect />,
  },
]);

export default router;
