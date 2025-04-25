import { useEffect } from "react";
import { useAuthStore } from "./auth/authStore";
import AppRoutes from "./routes/AppRoutes";
import { BrowserRouter } from "react-router-dom";
import { refreshAccessToken } from "./services/tokenService";

function App() {
  const { checkTokenValidity, logout, expiresAt, refreshToken, login } =
    useAuthStore();

  useEffect(() => {
    if (!expiresAt) return;

    if (!checkTokenValidity()) {
      if (refreshToken) {
        refreshAccessToken(refreshToken)
          .then((res) => {
            const { accessToken, expiresIn } = res;
            login(accessToken, refreshToken, expiresIn);
          })
          .catch(() => logout());
      } else {
        logout();
      }
    }
  }, [checkTokenValidity, logout, expiresAt, refreshToken, login]);

  return (
    <>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </>
  );
}

export default App;
