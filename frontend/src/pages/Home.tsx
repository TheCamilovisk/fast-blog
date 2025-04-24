import { useEffect, useState } from "react";
import { PostListItem, fetchPosts } from "../services/postService";
import { Link } from "react-router-dom";

const Home = () => {
  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [totalItems, setTotalItems] = useState(0);

  const limit = 10;

  useEffect(() => {
    const loadPosts = async () => {
      try {
        const data = await fetchPosts(offset, limit);
        setPosts(data.posts);
        setTotalItems(data.totalItems);
      } catch (error) {
        console.error("Error fetching posts:", error);
      }
    };

    loadPosts();
  }, [offset]);

  const totalPages = Math.ceil(totalItems / limit);

  return (
    <div>
      <h1>Blog Posts</h1>

      <ul>
        {posts.map((post) => (
          <li key={post.id}>
            <h2>
              <Link to={"/post/" + post.id}>{post.title}</Link>
            </h2>
            <p>
              <Link to={"/post/" + post.id}>{post.subtitle}</Link>
            </p>
            <small>
              by{" "}
              <Link to={"/author/" + post.author.id}>
                {post.author.username}
              </Link>{" "}
              on {new Date(post.createdAt).toLocaleDateString()}
            </small>
          </li>
        ))}
      </ul>

      <div>
        {Array.from({ length: totalPages }, (_, i) => (
          <button
            key={i}
            onClick={() => setOffset(i * limit)}
            disabled={offset === i * limit}
            style={{ margin: "0 0.25 rem" }}
          >
            {i + 1}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Home;
