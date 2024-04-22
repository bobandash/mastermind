import { createBrowserRouter } from "react-router-dom";
import HomePage from "./pages/Home";
import SingleplayerSelect from "./pages/SingleplayerSelect";
import Game from "./pages/Game";
import WaitingRoom from "./pages/WaitingRoom";

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
  {
    path: "/room/:roomId",
    element: <WaitingRoom />,
  },
]);

export default router;
