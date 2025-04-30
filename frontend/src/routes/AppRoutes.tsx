import { Routes, Route } from "react-router-dom";
import Layout from "../components/Layout";
import Post from "../pages/Post";
import Contact from "../pages/Contact";
import NotFound from "../pages/NotFound";
import Author from "../pages/Author";
import Login from "../pages/Login";
import Logout from "../pages/Logout";
import PostSearch from "../pages/PostSearch";
import About from "../pages/About";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<PostSearch />} />
        <Route path="post/:id" element={<Post />} />
        <Route path="author/:id" element={<Author />} />
        <Route path="contact" element={<Contact />} />
        <Route path="about" element={<About />} />
        <Route path="login" element={<Login />} />
        <Route path="logout" element={<Logout />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

export default App;
