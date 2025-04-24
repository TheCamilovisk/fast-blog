import { Link } from "react-router-dom";
import { useAuthStore } from "../auth/authStore";

const Header = () => {
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn());

  return (
    <header>
      <nav>
        <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/post">Post</Link>
          </li>
          <li>
            <Link to="/author">Author</Link>
          </li>
          <li>
            <Link to="/contact">Contact</Link>
          </li>
          <li>
            {isLoggedIn ? (
              <Link to="/logout">Logout</Link>
            ) : (
              <Link to="/login">Login</Link>
            )}
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
