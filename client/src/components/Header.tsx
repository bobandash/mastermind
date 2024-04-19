import { useNavigate } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();
  return (
    <header className="flex bg-gray-400">
      <div className="flex w-11/12 mx-auto py-2 justify-between">
        <button
          className="bg-white px-2 border-[1px] border-black rounded-lg"
          onClick={() => {
            navigate("/");
          }}
        >
          Home
        </button>
        <button className="bg-white px-2 border-[1px] border-black rounded-lg">
          Choose Name
        </button>
      </div>
    </header>
  );
};

export default Header;
