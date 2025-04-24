import { FormEvent, useState } from "react";
import { publicApi } from "../api/axios";
import { useAuthStore } from "../auth/authStore";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [identifier, setIdentifier] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string>("");
  const setTokens = useAuthStore((state) => state.setTokens);
  const navigate = useNavigate();

  const handleLogin = async (
    event: FormEvent<HTMLFormElement>
  ): Promise<void> => {
    event.preventDefault();

    const form = new URLSearchParams();
    form.append("username", identifier);
    form.append("password", password);

    setError("");

    try {
      const res = await publicApi.post("/auth/token", form, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      setTokens(res.data.access_token, res.data.refresh_token);
      navigate("/");
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (error: unknown) {
      setError("Invalid credentials");
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
