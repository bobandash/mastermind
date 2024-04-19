import { useEffect, useState } from "react";
import Header from "../components/Header";
import authAxios from "../httpClient";
import { useParams } from "react-router-dom";

const Game = () => {
  const [gameInfo, setGameInfo] = useState({
    isMultiplayer: false,
    gameHistory: [],
    numTurnsRemaining: 0,
    numColors: 0, // number of options the user has to choose from
  });
  const [currChoice, setCurrChoice] = useState([]);
  const { gameId, roundId } = useParams();

  useEffect(() => {
    async function getRoundDetails() {
      try {
        const response = await authAxios.get(`/api/rounds/${roundId}`);
        const data = response.data;
        const {
          is_multiplayer,
          round_ended,
          turn_history,
          turns_remaining,
          turns_used,
        } = data;

        console.log(response.data);
      } catch {
        console.error("Could not get round details, please try again later.");
      }
    }
    getRoundDetails();
  }, [roundId]);

  return (
    <div className="pb-10">
      <Header />
      <div className="w-11/12 max-w-[400px] mx-auto flex flex-col gap-8 pt-5 2xl:pt-8"></div>
    </div>
  );
};

function Color({ isClickable }) {
  return <div className="rounded-full"></div>;
}

export default Game;
