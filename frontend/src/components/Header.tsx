import { Link } from "react-router-dom";
import { useAuthStore } from "../auth/authStore";

const Header = () => {
  const isLoggedIn = useAuthStore((state) => state.checkTokenValidity());

  return (
    <header>
      <nav>
        <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/about">About</Link>
          </li>
          <li>
            <Link to="/contact">Contact</Link>
          </li>
        </ul>
      </nav>
      {isLoggedIn ? (
        <Link to="/logout">Logout</Link>
      ) : (
        <Link to="/login">Login</Link>
      )}
    </header>
  );
};

export default Header;
