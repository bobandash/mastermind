import { useEffect, useState } from "react";
import Header from "../components/Header";
import authAxios from "../httpClient";
import { useParams } from "react-router-dom";
import Loading from "./Loading";

// response_data = {
//     round: {
//         "id": round_id,
//         "turns_used": num_turns_used,
//         "turns_remaining": max_turns - num_turns_used,
//         "status": round.status.name,
//         "turn_history": turn_history,
//         "secret_code": secret_code,
//     },
//     game: {
//         "id": game.id,
//         "is_multiplayer": is_multiplayer,
//         "difficulty": {
//             "mode": mode,
//             "num_holes": num_holes,
//             "num_colors": num_colors,
//             "max_turns": max_turns,
//         },
//     },
// }

const Game = () => {
  const [gameInfo, setGameInfo] = useState({
    isMultiplayer: false,
    isRoundOver: false,
    turnHistory: [],
    numTurnsRemaining: 0,
    numTurnsUsed: 0,
    numColors: 0, // number of options the user has to choose from
    secretCode: null,
  });
  const [currChoice, setCurrChoice] = useState([]);
  const { roundId } = useParams();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function getRoundDetails() {
      try {
        const response = await authAxios.get(`/api/v1.0/rounds/${roundId}`);
        const data = response.data;
        console.log(data);
        const {
          is_multiplayer,
          round_ended,
          turn_history,
          turns_remaining,
          turns_used,
        } = data;
        setGameInfo((prevGameInfo) => ({
          ...prevGameInfo,
          isMultiplayer: is_multiplayer,
          isRoundOver: round_ended,
          turnHistory: turn_history,
          numTurnsRemaining: turns_remaining,
          numTurnsUsed: turns_used,
        }));
        setIsLoading(false);
      } catch {
        console.error("Could not get round details, please try again later.");
      }
    }
    getRoundDetails();
  }, [roundId]);

  if (isLoading) {
    <Loading />;
  }

  if (!gameInfo.isMultiplayer) {
    return (
      <div className="pb-10">
        <Header />
        <div className="w-11/12 max-w-[400px] mx-auto flex flex-col gap-8 pt-5 2xl:pt-8"></div>
      </div>
    );
  }
};

function Color({ isClickable }) {
  return <div className="rounded-full"></div>;
}

export default Game;
