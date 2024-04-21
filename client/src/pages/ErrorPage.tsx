import { FC } from "react";
import { useNavigate } from "react-router-dom";

interface ErrorPageProps {
  message: string;
  code: number;
}

const ErrorPage: FC<ErrorPageProps> = ({ message, code }) => {
  const navigate = useNavigate();
  function navigateHome() {
    navigate("/");
  }
  return (
    <div className="min-h-[100vh]">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-2">
        <h1 className="font-bold text-5xl">{code}</h1>
        <h2 className="text-2xl text-center">{message}</h2>
        <button
          className="text-2xl border-2 border-black px-2"
          onClick={navigateHome}
        >
          Home
        </button>
      </div>
    </div>
  );
};

export default ErrorPage;
