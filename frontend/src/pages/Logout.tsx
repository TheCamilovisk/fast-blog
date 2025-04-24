import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../auth/authStore";
import { useEffect } from "react";

const Logout = () => {
  const clearTokens = useAuthStore((state) => state.clearTokens);
  const navigate = useNavigate();

  useEffect(() => {
    clearTokens();
    navigate("/login");
  }, [clearTokens, navigate]);

  return <p>Logging out...</p>;
};

export default Logout;
