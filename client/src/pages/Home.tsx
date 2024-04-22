import { FormEvent, useEffect, useState } from "react";
import logo from "../assets/logo.jpg";
import Header from "../components/Header";
import { useNavigate } from "react-router-dom";
import authAxios from "../httpClient";
import { isAxiosError } from "axios";
const HomePage = () => {
  const navigate = useNavigate();
  const [isRulesVisible, setIsRulesVisible] = useState(true);
  const [code, setCode] = useState("");
  function toggleRulesVisible() {
    setIsRulesVisible((prev) => !prev);
  }
  const [error, setError] = useState("");
  useEffect(() => {
    async function register() {
      try {
        await authAxios.post("/api/v1.0/auth/register");
      } catch {
        console.error("Error: could not create a session");
      }
    }
    register();
  }, []);

  function redirectSinglePlayerSelect() {
    navigate("/singleplayer-select");
  }

  async function createLobby() {
    try {
      const response = await authAxios.post("/api/v1.0/rooms/");
      const roomId = response.data.id;
      navigate(`/room/${roomId}`);
    } catch {
      console.error("Error: could not create a session");
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setError("");
    setCode(e.target.value);
  }

  async function joinLobby(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      const response = await authAxios.post("/api/v1.0/rooms/join", {
        code: code,
      });
      const data = response.data;
      navigate(`/room/${data.id}`);
    } catch (error) {
      console.error("Error: Could not join");
      if (isAxiosError(error)) {
        setError(error.response?.data.error.message);
      }
    }
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
        <button
          className="bg-[#464242] hover:bg-[#5a5a5a] text-white transition-all text-4xl w-full mx-auto border-2 border-black py-2 rounded-xl"
          onClick={createLobby}
        >
          Create Lobby
        </button>
        <hr className="border-2 border-black" />
        <form className="flex flex-col gap-4" onSubmit={joinLobby}>
          <input
            type="text"
            className="transition-all text-3xl w-full mx-auto border-2 border-black py-2 rounded-xl text-center text-black"
            placeholder="Enter code"
            onChange={handleChange}
            value={code}
          />
          <button className="bg-[#464242] hover:bg-[#5a5a5a] text-white transition-all text-4xl w-full mx-auto border-2 border-black py-2 rounded-xl">
            Join Game
          </button>
        </form>
        {error && <h1 className="text-4xl text-center">{error}</h1>}
      </div>
    </div>
  );
};

export default HomePage;
