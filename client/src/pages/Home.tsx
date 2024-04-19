import { useEffect, useState } from "react";
import logo from "../assets/logo.jpg";
import axios from "axios";
import Header from "../components/Header";
import { useNavigate } from "react-router-dom";
const HomePage = () => {
  const navigate = useNavigate();
  const [isRulesVisible, setIsRulesVisible] = useState(true);
  function toggleRulesVisible() {
    setIsRulesVisible((prev) => !prev);
  }
  useEffect(() => {
    async function register() {
      try {
        await axios.post("/api/auth/register");
      } catch {
        console.error("Error: could not create a session");
      }
    }
    register();
  }, []);

  function redirectSinglePlayerSelect() {
    navigate("/singleplayer-select");
  }

  return (
    <div className="pb-10">
      <Header />
      <div className="w-11/12 max-w-[400px] mx-auto flex flex-col gap-8 pt-5 2xl:pt-8">
        {isRulesVisible && (
          <>
            <h1 className="text-center text-4xl font-bold">
              Mastermind Online
            </h1>
            <button
              className="bg-[#F24545] text-4xl w-full mx-auto text-white border-2 border-black py-2 rounded-xl hover:bg-[#f56262] transition-all"
              onClick={toggleRulesVisible}
            >
              Play
            </button>
            <div>
              <h2 className="font-bold text-lg">Rules:</h2>
              <p className="text-lg">
                Mastermind is an addictive puzzle game that you can spend a lot
                of time playing. Here, your task is to guess the color of the
                circles on the decoding board. At the beginning of the game, you
                will see a board with rows with empty circles each. The color
                pattern is encrypted, and your task is to guess what color each
                circle is and in what order the colors should be arranged. There
                are numerous colors to choose from, but be careful - each color
                can appear more than once in a row. When you crack the code, the
                game will be won. You have a limited to win the game, and after
                each failed attempt, you will receive colored hints (text taken
                from https://mastermindgame.org/).
              </p>
            </div>
          </>
        )}
        <img src={logo} alt="mastermind logo" />
        <button
          className="bg-[#F24545] text-4xl w-full mx-auto text-white border-2 border-black py-2 rounded-xl hover:bg-[#f56262] transition-all"
          onClick={redirectSinglePlayerSelect}
        >
          Single Player
        </button>
        <button className="bg-[#464242] text-4xl w-full mx-auto text-white border-2 border-black py-2 rounded-xl hover:bg-[#5a5a5a] transition-all">
          Multiplayer
        </button>
      </div>
    </div>
  );
};

export default HomePage;
