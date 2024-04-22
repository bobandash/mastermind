import { FC, useEffect, useMemo, useState } from "react";
import Header from "../components/Header";
import authAxios from "../httpClient";
import { useNavigate, useParams } from "react-router-dom";
import Loading from "./Loading";
import logo from "../assets/logo.jpg";
import axios from "axios";
import ErrorPage from "./ErrorPage";
import { socket } from "../socket";

//! TODO: If have time, combine the react pages for singleplayer and multiplayer, not too important though

const status = {
  NOT_STARTED: "NOT_STARTED",
  IN_PROGRESS: "IN_PROGRESS",
  COMPLETED: "COMPLETED",
  TERMINATED: "TERMINATED",
};

const DIFFICULTIES = {
  NORMAL: "NORMAL",
  HARD: "HARD",
  CUSTOM: "CUSTOM",
};

interface GameRowProps {
  data: TurnHistory;
}

interface EmptyGameRowProps {
  numHoles: number;
}

type TurnHistory = {
  guess: number[];
  result: {
    black_pegs: number;
    message: string;
    white_pegs: number;
    won_round: boolean;
  };
  turn_num: number;
};

type RoundInfoState = {
  status: string;
  turnHistory: TurnHistory[];
  numTurnsRemaining: number;
  numTurnsUsed: number;
  numColors: number;
  secretCode: null | number[];
  feedback: string;
};

type ErrorProps = {
  code: null | number;
  message: null | string;
};

const GameRow: FC<GameRowProps> = ({ data }) => {
  const { guess, result } = data;
  const numCols = guess.length + 1;
  const numColsPeg = Math.min(Math.round(guess.length / 2), 3);
  const gridTemplateColumnsRow = `repeat(${numCols}, 1fr)`;
  const gridTemplateColumnsPegs = `repeat(${numColsPeg}, 1fr)`;
  const { black_pegs, white_pegs } = result;
  const empty_pegs = guess.length - black_pegs - white_pegs;

  const blackPegArr = Array(black_pegs).fill(0);
  const whitePegArr = Array(white_pegs).fill(0);
  const emptyPegArr = Array(empty_pegs).fill(0);
  return (
    <div
      className="w-full gap-2 gap-y-3 py-1"
      style={{
        display: "grid",
        gridTemplateColumns: gridTemplateColumnsRow,
      }}
    >
      <div
        className="bg-[#8f8e8e] w-full aspect-square mx-auto relative max-w-[40px] gap-2 gap-y-3 p-1"
        style={{
          display: "grid",
          gridTemplateColumns: gridTemplateColumnsPegs,
        }}
      >
        {blackPegArr.map((_value, index) => (
          <div
            key={index}
            className="bg-black aspect-square w-full rounded-full min-w-[4px]"
          ></div>
        ))}
        {whitePegArr.map((_value, index) => (
          <div
            key={index}
            className="bg-white aspect-square w-full rounded-full  min-w-[4px]"
          ></div>
        ))}
        {emptyPegArr.map((_value, index) => (
          <div
            key={index}
            className="bg-gray-500 aspect-square w-full rounded-full  min-w-[4px]"
          ></div>
        ))}
      </div>
      {guess.map((value, index) => (
        <div
          className="bg-white rounded-full w-full aspect-square mx-auto relative max-w-[40px]"
          key={index}
        >
          <p className="absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2">
            {value}
          </p>
        </div>
      ))}
    </div>
  );
};

const EmptyGameRow: FC<EmptyGameRowProps> = ({ numHoles }) => {
  const numCols = numHoles + 1;
  const gridTemplateColumnsRow = `repeat(${numCols}, 1fr)`;
  const emptyHoles = Array(numHoles).fill(0);
  return (
    <div
      className="w-full gap-2 gap-y-3 py-1"
      style={{
        display: "grid",
        gridTemplateColumns: gridTemplateColumnsRow,
      }}
    >
      <div
        className="bg-[#8f8e8e] w-full aspect-square mx-auto relative max-w-[40px] gap-2 gap-y-3 p-1"
        style={{
          display: "grid",
          gridTemplateColumns: gridTemplateColumnsRow,
        }}
      ></div>
      {emptyHoles.map((_value, index) => (
        <div
          className="bg-white rounded-full w-full aspect-square mx-auto relative max-w-[40px]"
          key={index}
        ></div>
      ))}
    </div>
  );
};

type UserInfoProps = {
  id: string;
  isCodeBreaker: boolean;
};

const MultiplayerGame = () => {
  const navigate = useNavigate();
  const { gameId, roundId } = useParams();
  const socketRoomId = `game_${gameId}_round_${roundId}`;

  // All socket logic
  socket.on("connect", () => {
    console.log("Connected to server");
  });

  socket.on("disconnect", (reason) => {
    console.log(reason);
  });

  socket.on("start_round", (data) => {
    const { status } = data;
    setRoundInfo((prevRoundInfo) => ({
      ...prevRoundInfo,
      status: status,
    }));
  });

  socket.on("new_move_info", (data) => {
    const { round_info } = data;
    setRoundInfo((prevRoundInfo) => ({
      ...prevRoundInfo,
      ...round_info,
    }));
  });

  socket.on("new_round_info", (data) => {
    const { game_id, round_id } = data;
    navigate(`/multiplayerGame/${game_id}/rounds/${round_id}`);
  });

  const [roundInfo, setRoundInfo] = useState<RoundInfoState>({
    status: status.IN_PROGRESS,
    turnHistory: [],
    numTurnsRemaining: 0,
    numTurnsUsed: 0,
    numColors: 0, // number of options the user has to choose from
    secretCode: null,
    feedback: "Make your move.",
  });
  // Not related to the turn
  const [gameSettings, setGameSettings] = useState({
    maxTurns: 0,
    numColors: 0,
    numHoles: 0,
    isMultiplayer: false,
    mode: DIFFICULTIES.HARD,
    numRounds: 0,
  });
  const [userInfo, setUserInfo] = useState<UserInfoProps>({
    id: "",
    isCodeBreaker: false, // if false, that means user is code maker
  });
  const [gameStatus, setGameStatus] = useState({
    rounds: [],
    status: status.NOT_STARTED,
  });
  const [currChoice, setCurrChoice] = useState<number[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<ErrorProps>({ code: null, message: null });
  const [currSecretCodeSelection, setCurrSecretCodeSelection] = useState<
    number[]
  >([]);

  useEffect(() => {
    async function getGameInfo() {
      try {
        const roundRes = await authAxios.get(`/api/v1.0/rounds/${roundId}`, {
          params: { game_id: gameId },
        });
        const gameRes = await authAxios.get(`/api/v1.0/games/${gameId}`);
        const userRes = await authAxios.get("/api/v1.0/users/me");
        const userResData = userRes.data;
        const { code_breaker_id } = roundRes.data;
        const isCodeBreaker = code_breaker_id === userRes.data.id;
        setUserInfo({
          id: userResData.id,
          isCodeBreaker: isCodeBreaker,
        });
        const roundData = roundRes.data;
        const { difficulty, rounds, status, is_multiplayer, num_rounds } =
          gameRes.data;
        let feedback =
          roundData?.turns[roundData.turns.length - 1]?.result?.message ??
          "Make your move.";
        if (!isCodeBreaker) {
          feedback = "Waiting for player to make their move";
        }
        setGameStatus((prevSettings) => ({
          ...prevSettings,
          rounds: rounds,
          status: status,
        }));
        setGameSettings((prevSettings) => ({
          ...prevSettings,
          maxTurns: difficulty.max_turns,
          mode: difficulty.mode,
          numColors: difficulty.num_colors,
          numHoles: difficulty.num_holes,
          isMultiplayer: is_multiplayer,
          numRounds: num_rounds,
        }));
        setRoundInfo((prevRoundInfo) => ({
          ...prevRoundInfo,
          secretCode: roundData.secret_code,
          status: roundData.status,
          turnHistory: roundData.turns,
          numTurnsRemaining: roundData.turns_remaining,
          numTurnsUsed: roundData.turns_used,
          feedback: feedback,
        }));
        socket.emit("join_multiplayer_round", {
          room: socketRoomId,
        });
        setIsLoading(false);
      } catch (error) {
        if (axios.isAxiosError(error)) {
          const status = error.response?.status;
          const message = error.response?.data.error.message;
          if (status && message) {
            setError({
              code: status,
              message: message,
            });
          }
          console.error("Could not get round details, please try again later.");
        }
      }
    }
    getGameInfo();
  }, [roundId, gameId, socketRoomId]);

  async function createNewRound() {
    const roundResponse = await authAxios.post(
      `/api/v1.0/games/${gameId}/rounds`
    );
    const roundId = roundResponse.data.id;
    socket.emit("create_new_round", {
      room: socketRoomId,
      game_id: gameId,
      round_id: roundId,
    });
    navigate(`/multiplayerGame/${gameId}/rounds/${roundId}`);
  }

  // Choices start starts at 0
  const colorOptions = useMemo(() => {
    const res = [];
    for (let i = 0; i < gameSettings.numColors; i++) {
      res.push(i);
    }
    return res;
  }, [gameSettings]);

  const possibleHoles = useMemo(() => {
    const res = [];
    for (let i = 0; i < gameSettings.numHoles; i++) {
      res.push(i);
    }
    return res;
  }, [gameSettings]);
  const gridTemplateColumnsValue = `repeat(${gameSettings.numHoles}, 1fr)`;
  const emptyRowsArr = Array(roundInfo.numTurnsRemaining).fill(0);

  function handleOptionClick(number: number) {
    setCurrChoice([...currChoice, number]);
  }

  function handleClear() {
    setCurrChoice([]);
  }

  function handleClearSecretCodeSelection() {
    setCurrSecretCodeSelection([]);
  }

  function handleSecretCodeOptionClick(number: number) {
    setCurrSecretCodeSelection([...currSecretCodeSelection, number]);
  }

  async function handleAddSecretCode() {
    try {
      await authAxios.patch(`/api/v1.0/rounds/${roundId}/secret-code`, {
        secret_code: currSecretCodeSelection,
      });
      const inProgress = status.IN_PROGRESS;
      setRoundInfo((prevRoundInfo) => ({
        ...prevRoundInfo,
        status: inProgress,
        secretCode: currSecretCodeSelection,
        feedback: "Waiting for player to make their move.",
      }));
      socket.emit("add_secret_code", {
        room: socketRoomId,
        status: inProgress,
      });
    } catch {
      console.error("Could not add secret code");
    }
  }

  async function handleMakeMove(e: React.MouseEvent<HTMLButtonElement>) {
    e.preventDefault();
    try {
      const response = await authAxios.post(
        `/api/v1.0/rounds/${roundId}/turns`,
        {
          guess: currChoice,
        }
      );
      const data = response.data;
      const numTurnsRemaining = gameSettings.maxTurns - data.turn_num;
      const { message, won_round } = data.result;
      let secretCode = null;
      const isRoundOver = won_round || numTurnsRemaining === 0;

      if (isRoundOver) {
        const response = await authAxios.get(
          `/api/v1.0/rounds/${roundId}/secret-code`
        );
        const data = response.data;
        secretCode = data.secret_code;
      }
      setCurrChoice([]);
      const newRoundInfo = {
        feedback: `${message}`,
        status: isRoundOver ? status.COMPLETED : status.IN_PROGRESS,
        turnHistory: [...roundInfo.turnHistory, data],
        numTurnsRemaining: numTurnsRemaining,
        numTurnsUsed: data.turn_num,
      };
      setRoundInfo((prevRoundInfo) => ({
        ...prevRoundInfo,
        ...newRoundInfo,
        secretCode: secretCode,
      }));
      socket.emit("make_move", {
        room: socketRoomId,
        round_info: newRoundInfo,
      });
    } catch {
      console.error("Could not make move.");
    }
  }

  const optionBtnDisabled =
    roundInfo.status !== status.IN_PROGRESS ||
    roundInfo.numTurnsRemaining === 0 ||
    currChoice.length === gameSettings.numHoles ||
    !userInfo.isCodeBreaker;

  const secretCodeOptionBtnDisabled =
    currSecretCodeSelection.length === gameSettings.numHoles;

  const makeMoveBtnDisabled =
    roundInfo.status !== status.IN_PROGRESS ||
    roundInfo.numTurnsRemaining === 0 ||
    currChoice.length !== gameSettings.numHoles ||
    !userInfo.isCodeBreaker;

  if (isLoading) {
    <Loading />;
  }

  if (error.code && error.message) {
    return <ErrorPage code={error.code} message={error.message} />;
  }

  if (roundInfo.status === status.NOT_STARTED && userInfo.isCodeBreaker) {
    return (
      <div className="w-full min-h-[100vh] flex items-center justify-center">
        <h1 className="font-bold text-4xl text-center">
          Waiting for other user to decide secret code....
        </h1>
      </div>
    );
  }

  if (roundInfo.status === status.NOT_STARTED && !userInfo.isCodeBreaker) {
    return (
      <div className="w-11/12 max-w-[500px] mx-auto min-h-[100vh] flex flex-col items-center justify-center gap-4">
        <h1 className="font-bold text-4xl text-center">
          Decide on the secret code.
        </h1>
        <div className="bg-[#d8cfc9] w-full">
          <div className="w-11/12 mx-auto py-3 flex flex-col gap-2">
            <h2 className="font-bold text-center underline">
              Current Selection
            </h2>
            <div
              className="w-full gap-2 gap-y-3"
              style={{
                display: "grid",
                gridTemplateColumns: gridTemplateColumnsValue,
              }}
            >
              {possibleHoles.map((_value, index) => (
                <div
                  className="bg-white rounded-full w-full aspect-square mx-auto relative max-w-[40px]"
                  key={index}
                >
                  <p className="absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2">
                    {currSecretCodeSelection[index] ?? ""}
                  </p>
                </div>
              ))}
            </div>
            <div className="flex gap-4 justify-center">
              <button
                className="border-2 border-black px-2 bg-white rounded-sm hover:bg-gray-200 transition-all"
                onClick={handleClearSecretCodeSelection}
              >
                Clear
              </button>
              <button
                className="border-2 border-black px-2 bg-[#464242] hover:bg-[#5a5a5a] text-white transition-all disabled:cursor-not-allowed"
                onClick={handleAddSecretCode}
              >
                Choose Secret Code
              </button>
            </div>
          </div>
        </div>
        <div className=" border-black border-2 py-3 mt-2 bg-black w-full">
          <div className="w-11/12 mx-auto flex flex-col gap-2">
            <h2 className="font-bold text-white text-center underline">
              Options To Choose From
            </h2>
            <div className="grid grid-cols-4 gap-2 gap-y-3">
              {colorOptions.map((value, index) => (
                <button
                  className="bg-white rounded-full w-[40px] h-[40px] mx-auto disabled:cursor-not-allowed"
                  key={index}
                  disabled={secretCodeOptionBtnDisabled}
                  onClick={() => {
                    handleSecretCodeOptionClick(value);
                  }}
                >
                  {value}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="pb-10 flex flex-col">
      <Header />
      <div className="w-11/12 max-w-[500px] mx-auto h-full flex-grow">
        <img src={logo} alt="mastermind logo" className="my-3" />
        <div className="bg-white border-2 border-black text-center">
          {roundInfo.feedback}
        </div>
        {roundInfo.secretCode && (
          <div className="bg-black border-2 border-black text-center py-3 flex flex-col gap-2">
            <h2 className="font-bold text-center underline text-white">
              Secret Code
            </h2>
            <div
              className=" gap-2 gap-y-3 w-11/12 mx-auto"
              style={{
                display: "grid",
                gridTemplateColumns: gridTemplateColumnsValue,
              }}
            >
              {roundInfo.secretCode.map((value, index) => (
                <div
                  className="bg-white rounded-full w-full aspect-square mx-auto relative max-w-[40px]"
                  key={index}
                >
                  <p className="absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2">
                    {value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
        <div className="bg-[#d18b5f] py-3 flex flex-col gap-2">
          <h2 className="font-bold text-center underline">Game History</h2>
          {emptyRowsArr.map((_, index) => (
            <EmptyGameRow key={index} numHoles={gameSettings.numHoles} />
          ))}
          {roundInfo.turnHistory
            .slice()
            .reverse()
            .map((turn, index) => (
              <GameRow key={index} data={turn} />
            ))}
        </div>
        <div className="bg-[#d8cfc9]">
          <div className="w-11/12 mx-auto py-3 flex flex-col gap-2">
            <h2 className="font-bold text-center underline">
              Current Selection
            </h2>
            <div
              className="w-full gap-2 gap-y-3"
              style={{
                display: "grid",
                gridTemplateColumns: gridTemplateColumnsValue,
              }}
            >
              {possibleHoles.map((_value, index) => (
                <div
                  className="bg-white rounded-full w-full aspect-square mx-auto relative max-w-[40px]"
                  key={index}
                >
                  <p className="absolute top-1/2 left-1/2 -translate-y-1/2 -translate-x-1/2">
                    {currChoice[index] ?? ""}
                  </p>
                </div>
              ))}
            </div>
            <div className="flex gap-4 justify-center">
              <button
                className="border-2 border-black px-2 bg-white rounded-sm hover:bg-gray-200 transition-all"
                onClick={handleClear}
                disabled={!userInfo.isCodeBreaker}
              >
                Clear
              </button>
              <button
                className="border-2 border-black px-2 bg-[#464242] hover:bg-[#5a5a5a] text-white transition-all disabled:cursor-not-allowed"
                onClick={handleMakeMove}
                disabled={makeMoveBtnDisabled}
              >
                Make move
              </button>
            </div>
          </div>
          <div className=" border-black border-2 py-3 mt-2 bg-black">
            <div className="w-11/12 mx-auto flex flex-col gap-2">
              <h2 className="font-bold text-white text-center underline">
                Options To Choose From
              </h2>
              <div className="grid grid-cols-4 gap-2 gap-y-3">
                {colorOptions.map((value, index) => (
                  <button
                    className="bg-white rounded-full w-[40px] h-[40px] mx-auto disabled:cursor-not-allowed"
                    key={index}
                    disabled={optionBtnDisabled}
                    onClick={() => {
                      handleOptionClick(value);
                    }}
                  >
                    {value}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
        {roundInfo.status === status.COMPLETED && (
          <div className="flex flex-row gap-4 justify-around bg-yellow-200 py-3">
            <button
              className="bg-white p-3 border-black border-2"
              onClick={() => {
                navigate("/");
              }}
            >
              Back Home
            </button>
            {gameStatus.rounds.length < gameSettings.numRounds && (
              <button
                className="bg-white p-3 border-black border-2"
                onClick={createNewRound}
              >
                Next Round
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiplayerGame;
