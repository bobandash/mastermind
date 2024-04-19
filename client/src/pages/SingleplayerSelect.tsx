import { useMemo, useState } from "react";
import Header from "../components/Header";
import logo from "../assets/logo.jpg";
import authAxios from "../httpClient";
import { useNavigate } from "react-router-dom";
const DIFFICULTIES = {
  NORMAL: "NORMAL",
  HARD: "HARD",
  CUSTOM: "CUSTOM",
};

const SingleplayerSelect = () => {
  const navigate = useNavigate();
  const [settings, setSettings] = useState({
    isMultiplayer: false,
    difficulty: DIFFICULTIES.NORMAL,
    maxTurns: 8,
    numHoles: 4,
    numColors: 8,
  });

  async function createSinglePlayerGame(e: React.FormEvent<HTMLFormElement>) {
    try {
      e.preventDefault();
      const { difficulty, maxTurns, numHoles, numColors } = settings;
      const gameResponse = await authAxios.post("/api/games", {
        is_multiplayer: false,
        difficulty: difficulty,
        max_turns: maxTurns,
        num_holes: numHoles,
        num_colors: numColors,
      });
      const gameId = gameResponse.data.id;
      const roundResponse = await authAxios.post(`/api/games/${gameId}/rounds`);
      const roundId = roundResponse.data.round_data.id;
      navigate(`/games/${gameId}/rounds/${roundId}`);
    } catch {
      console.error("Failed to create game.");
    }
  }

  const maxTurnRange = useMemo(() => {
    const res = [];
    for (let i = 8; i <= 20; i++) {
      res.push(i);
    }
    return res;
  }, []);

  const numHolesRange = useMemo(() => {
    const res = [];
    for (let i = 4; i <= 10; i++) {
      res.push(i);
    }
    return res;
  }, []);

  const numColorsRange = useMemo(() => {
    const res = [];
    for (let i = 8; i <= 20; i++) {
      res.push(i);
    }
    return res;
  }, []);

  const handleChangeDifficulty = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (e.target.value === DIFFICULTIES.CUSTOM) {
      setSettings({ ...settings, difficulty: e.target.value });
    } else if (e.target.value === DIFFICULTIES.NORMAL) {
      setSettings({
        ...settings,
        difficulty: e.target.value,
        maxTurns: 8,
        numHoles: 4,
        numColors: 8,
      });
    } else if (e.target.value === DIFFICULTIES.HARD) {
      setSettings({
        ...settings,
        difficulty: e.target.value,
        maxTurns: 12,
        numHoles: 5,
        numColors: 10,
      });
    }
  };

  const handleChangeMaxTurns = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSettings({ ...settings, maxTurns: Number(e.target.value) });
  };

  const handleChangeNumHoles = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSettings({ ...settings, numHoles: Number(e.target.value) });
  };

  const handleChangeNumColors = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSettings({ ...settings, numColors: Number(e.target.value) });
  };

  return (
    <div className="pb-10">
      <Header />
      <div className="w-11/12 max-w-[400px] mx-auto flex flex-col gap-8 pt-5 2xl:pt-8">
        <div className="flex flex-col gap-3">
          <img src={logo} alt="mastermind logo" />
          <h1 className="text-center text-4xl font-bold">Single Player Mode</h1>
        </div>
        <form className="flex flex-col gap-6" onSubmit={createSinglePlayerGame}>
          <div className="flex flex-col gap-1">
            <label htmlFor="difficulty" className="text-2xl font-bold">
              Difficulty:
            </label>
            <select
              name="difficulty"
              className="border-2 border-black text-3xl pl-1"
              value={settings.difficulty}
              onChange={handleChangeDifficulty}
            >
              <option value={DIFFICULTIES.NORMAL}>{DIFFICULTIES.NORMAL}</option>
              <option value={DIFFICULTIES.HARD}>{DIFFICULTIES.HARD}</option>
              <option value={DIFFICULTIES.CUSTOM}>{DIFFICULTIES.CUSTOM}</option>
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="difficulty" className="text-2xl font-bold">
              Max Turns:
            </label>
            <select
              name="maxTurns"
              className="border-2 border-black text-3xl pl-1"
              value={settings.maxTurns}
              onChange={handleChangeMaxTurns}
              disabled={settings.difficulty !== DIFFICULTIES.CUSTOM}
            >
              {maxTurnRange.map((value, index) => (
                <option value={value} key={index}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="difficulty" className="text-2xl font-bold">
              Number of Holes:
            </label>
            <select
              name="numHoles"
              className="border-2 border-black text-3xl pl-1"
              value={settings.numHoles}
              onChange={handleChangeNumHoles}
              disabled={settings.difficulty !== DIFFICULTIES.CUSTOM}
            >
              {numHolesRange.map((value, index) => (
                <option value={value} key={index}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="difficulty" className="text-2xl font-bold">
              Number of Colors:
            </label>
            <select
              name="numColors"
              className="border-2 border-black text-3xl pl-1"
              value={settings.numColors}
              onChange={handleChangeNumColors}
              disabled={settings.difficulty !== DIFFICULTIES.CUSTOM}
            >
              {numColorsRange.map((value, index) => (
                <option value={value} key={index}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <button className="bg-[#F24545] text-4xl w-full mx-auto text-white border-2 border-black py-2 rounded-xl hover:bg-[#f56262] transition-all uppercase disabled:text-[#c5c5c5] disabled:border-[#c5c5c5]">
            Start Game
          </button>
        </form>
      </div>
    </div>
  );
};

export default SingleplayerSelect;
