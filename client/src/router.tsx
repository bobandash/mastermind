import { createBrowserRouter } from "react-router-dom";
import HomePage from "./pages/Home";
import SingleplayerSelect from "./pages/SingleplayerSelect";
import Game from "./pages/Game";
import WaitingRoom from "./pages/WaitingRoom";
import MultiplayerGame from "./pages/MultiplayerGame";

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
    path: "/multiplayerGame/:gameId/rounds/:roundId",
    element: <MultiplayerGame />,
  },
  {
    path: "/room/:roomId",
    element: <WaitingRoom />,
  },
]);

export default router;
