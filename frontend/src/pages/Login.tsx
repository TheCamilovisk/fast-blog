import { FormEvent, useState } from "react";
import { useAuthStore } from "../auth/authStore";
import { useNavigate } from "react-router-dom";
import { getTokens } from "../services/tokenService";

const Login = () => {
  const [identifier, setIdentifier] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string>("");
  const setTokens = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const handleLogin = async (
    event: FormEvent<HTMLFormElement>
  ): Promise<void> => {
    event.preventDefault();

    setError("");

    try {
      const { accessToken, refreshToken, expiresIn } = await getTokens(
        identifier,
        password
      );

      setTokens(accessToken, refreshToken, expiresIn);
      navigate("/");
    } catch (error: unknown) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Invalid credentials");
      }
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <h2>Login</h2>
      <input
        placeholder="Username or Email"
        value={identifier}
        onChange={(e) => setIdentifier(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p>{error}</p>}
      <button type="submit">Login</button>
    </form>
  );
};

export default Login;
