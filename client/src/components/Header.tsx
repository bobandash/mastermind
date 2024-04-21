import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [usernameField, setUsernameField] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function getUsername() {
      try {
        const response = await axios.get("/api/v1.0/users/me");
        setUsername(response.data.username);
      } catch {
        console.error("Could not get username");
      }
    }
    getUsername();
  }, []);

  function togglePopup() {
    setIsPopupOpen((prev) => !prev);
    setError("");
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!(usernameField && usernameField.length < 20)) {
      setError("Needs to be 1-20 characters");
      return;
    }

    try {
      const response = await axios.patch(
        "/api/v1.0/users/me/username",
        {
          username: usernameField,
        },
        {
          withCredentials: true,
        }
      );
      if (response.status === 200) {
        setUsername(usernameField);
        setIsPopupOpen(false);
      }
    } catch (error) {
      setError("There was an error processing.");
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setError("");
    setUsernameField(e.target.value);
  }

  return (
    <header className="flex bg-gray-400">
      <div className="flex w-11/12 mx-auto py-2 justify-between relative">
        <button
          className="bg-white px-2 border-[1px] border-black rounded-lg"
          onClick={() => {
            navigate("/");
          }}
        >
          Home
        </button>
        {username === "" ? (
          <div>
            <button
              className="bg-white px-2 border-[1px] border-black rounded-lg"
              onClick={togglePopup}
            >
              Choose Name
            </button>
          </div>
        ) : (
          <p
            className="text-bold text-red-500 hover:cursor-pointer"
            onClick={togglePopup}
          >
            {username}
          </p>
        )}
        {isPopupOpen && (
          <form
            className="absolute bg-white right-0 top-6 flex flex-col p-2 border-black border-2 rounded-lg mt-4"
            onSubmit={async (e: React.FormEvent<HTMLFormElement>) => {
              e.preventDefault();
              await handleSubmit(e);
            }}
          >
            <label htmlFor="difficulty" className="text-sm font-bold">
              Username:
            </label>
            <input
              type="text"
              onChange={handleChange}
              className="border-[1px] border-black pl-1 text-sm"
            />
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <div className="flex flex-row mt-2 gap-2 justify-end">
              <button
                className="text-sm border-[1px] border-black rounded-sm px-2 font-bold"
                type="submit"
              >
                Confirm
              </button>
              <button
                className="text-sm border-[1px] border-black rounded-sm px-2"
                onClick={togglePopup}
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </header>
  );
};

export default Header;
