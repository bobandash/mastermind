import { useEffect, useMemo, useState } from "react";
import Header from "../components/Header";
import logo from "../assets/logo.jpg";
import authAxios from "../httpClient";
import { useNavigate, useParams } from "react-router-dom";
import { socket } from "../socket";
import ErrorPage from "./ErrorPage";

const DIFFICULTIES = {
  NORMAL: "NORMAL",
  HARD: "HARD",
  CUSTOM: "CUSTOM",
};

type userProps = {
  username: string;
  id: string;
};

const WaitingRoom = () => {
  const navigate = useNavigate();
  const [settings, setSettings] = useState({
    isMultiplayer: false,
    difficulty: DIFFICULTIES.NORMAL,
    maxTurns: 10,
    numHoles: 4,
    numColors: 8,
    numRounds: 2,
  });
  const [isHost, setIsHost] = useState(false);
  const [users, setUsers] = useState<userProps[]>([]);
  const [code, setCode] = useState("");
  const { roomId } = useParams();
  const waitingRoomId = "waiting_room_" + roomId; // !For passing in socket room
  const [error, setError] = useState(false);

  socket.on("connect", () => {
    console.log("Connected to server");
  });

  // CASE: handle unexpected disconnects
  // TODO: come back to disconnect exception
  socket.on("disconnect", (reason) => {
    console.log(reason);
  });

  socket.on("user_joined", (data) => {
    setUsers(data);
    // socket.emit("init_game_settings", {
    //   room: waitingRoomId,
    //   settings: settings,
    // });
  });

  socket.on("game_settings", (data) => {
    setSettings(data);
  });

  useEffect(() => {
    async function getWaitingRoomInfo() {
      try {
        const response = await authAxios.get(`/api/v1.0/rooms/${roomId}`);
        const userResponse = await authAxios.get("/api/v1.0/users/me");
        const data = response.data;
        const userData = userResponse.data;
        setIsHost(userData.is_host);
        setCode(data.code);
        setUsers(data.players);
        socket.emit("waiting_room", {
          room: waitingRoomId,
          players: data.players,
        });
      } catch {
        setError(true);
      }
    }
    getWaitingRoomInfo();
  }, [roomId, waitingRoomId]);

  async function createMultiplayerGame(e: React.FormEvent<HTMLFormElement>) {
    try {
      e.preventDefault();
      const { difficulty, maxTurns, numHoles, numColors } = settings;
      const gameResponse = await authAxios.post("/api/v1.0/games", {
        is_multiplayer: false,
        difficulty: difficulty,
        max_turns: maxTurns,
        num_holes: numHoles,
        num_colors: numColors,
      });
      const gameId = gameResponse.data.id;
      const roundResponse = await authAxios.post(
        `/api/v1.0/games/${gameId}/rounds`
      );
      const roundId = roundResponse.data.id;
      navigate(`/games/${gameId}/rounds/${roundId}`);
    } catch {
      console.error("Failed to create game.");
    }
  }

  const maxTurnRange = useMemo(() => {
    const res = [];
    for (let i = 10; i <= 20; i++) {
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
    for (let i = 10; i <= 20; i++) {
      res.push(i);
    }
    return res;
  }, []);

  const numRoundsRange = [2, 4, 6, 8];
  const handleSettingsChange = async (
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    if (!isHost) {
      return;
    }

    const { name, value } = e.target;
    let newSettings;
    if (name === "difficulty") {
      if (value === DIFFICULTIES.CUSTOM) {
        newSettings = { ...settings, difficulty: e.target.value };
      } else if (value === DIFFICULTIES.NORMAL) {
        newSettings = {
          ...settings,
          difficulty: e.target.value,
          maxTurns: 10,
          numHoles: 4,
          numColors: 8,
        };
      } else {
        newSettings = {
          ...settings,
          difficulty: e.target.value,
          maxTurns: 12,
          numHoles: 5,
          numColors: 10,
        };
      }
    } else {
      newSettings = { ...settings, [name]: Number(e.target.value) };
    }

    setSettings({ ...newSettings });
    const response = await authAxios.patch(`/api/v1.0/rooms/${roomId}`, {
      difficulty: newSettings.difficulty,
      max_turns: newSettings.maxTurns,
      num_holes: newSettings.numHoles,
      num_colors: newSettings.numColors,
      rounds: newSettings.numRounds,
    });
    console.log(response);
    socket.emit("change_game_settings", {
      room: waitingRoomId,
      settings: newSettings,
    });
  };

  if (error === true) {
    return <ErrorPage message={"Unauthorized"} code={401} />;
  }

  return (
    <div className="pb-10">
      <Header />
      <div className="w-11/12 max-w-[400px] mx-auto flex flex-col gap-8 pt-5 2xl:pt-8">
        <div className="flex flex-col gap-3">
          <img src={logo} alt="mastermind logo" />
          <h1 className="text-center text-4xl font-bold">Multiplayer Mode</h1>
          {users && (
            <h1 className="text-center text-4xl font-bold">
              {users.length}/2 Players
            </h1>
          )}
          {users && (
            <>
              <h2 className="text-center text-4xl font-bold">Players</h2>
              {users.map((user, index) => (
                <h3 className="text-center text-4xl" key={index}>
                  {user?.username ?? "Anonymous"}
                </h3>
              ))}
            </>
          )}
          {code && (
            <h2 className="text-center text-4xl font-bold border-2 border-black">
              {code}
            </h2>
          )}
        </div>
        <form className="flex flex-col gap-6" onSubmit={createMultiplayerGame}>
          <div className="flex flex-col gap-1">
            <label htmlFor="difficulty" className="text-2xl font-bold">
              Difficulty:
            </label>
            <select
              name="difficulty"
              className="border-2 border-black text-3xl pl-1"
              value={settings.difficulty}
              onChange={handleSettingsChange}
              disabled={!isHost}
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
              onChange={handleSettingsChange}
              disabled={!isHost || settings.difficulty !== DIFFICULTIES.CUSTOM}
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
              onChange={handleSettingsChange}
              disabled={!isHost || settings.difficulty !== DIFFICULTIES.CUSTOM}
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
              onChange={handleSettingsChange}
              disabled={!isHost || settings.difficulty !== DIFFICULTIES.CUSTOM}
            >
              {numColorsRange.map((value, index) => (
                <option value={value} key={index}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="difficulty" className="text-2xl font-bold">
              Number of Rounds:
            </label>
            <select
              name="numRounds"
              className="border-2 border-black text-3xl pl-1"
              value={settings.numRounds}
              onChange={handleSettingsChange}
              disabled={!isHost}
            >
              {numRoundsRange.map((value, index) => (
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

export default WaitingRoom;
