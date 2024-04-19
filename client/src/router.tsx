import { createBrowserRouter } from "react-router-dom";
import HomePage from "./pages/Home";
import SingleplayerSelect from "./pages/SingleplayerSelect";
import Game from "./pages/Game";

const router = createBrowserRouter([
  {
    path: "/",
    element: <HomePage />,
  },
  {
    path: "/singleplayer-select",
    element: <SingleplayerSelect />,
  },
  {
    path: "/games/:gameId/rounds/:roundId",
    element: <Game />,
  },
]);

export default router;
