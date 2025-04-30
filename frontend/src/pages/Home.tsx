import { useEffect, useState } from "react";
import { PostListItem, fetchPosts } from "../services/postService";
import PostList from "../components/posts/PostList";
import Pagination from "../components/Pagination";

const Home = () => {
  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [totalItems, setTotalItems] = useState(0);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const limit = 10;

  useEffect(() => {
    const loadPosts = async () => {
      try {
        const data = await fetchPosts(offset, limit);
        setPosts(data.posts);
        setTotalItems(data.totalItems);
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message);
        } else {
          setError("Internal server error");
        }
      } finally {
        setLoading(false);
      }
    };

    loadPosts();
  }, [offset]);

  if (loading) return <p>Loading posts...</p>;
  if (error) return <p>{error}</p>;
  if (!posts) return <p>Posts not found</p>;

  const totalPages = Math.ceil(totalItems / limit);

  return (
    <div>
      <h1>Blog Posts</h1>

      <PostList posts={posts} />

      <Pagination
        totalPages={totalPages}
        limit={limit}
        offset={offset}
        handleNavigation={setOffset}
      />
    </div>
  );
};

export default Home;
