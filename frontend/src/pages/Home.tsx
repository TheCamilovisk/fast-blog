import { useEffect, useState } from "react";
import { PostListItem, fetchPosts } from "../services/postService";
import PostList from "../components/PostList";
import Pagination from "../components/Pagination";

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

      <PostList posts={posts} />

      <Pagination
        totalPages={totalPages}
        limit={limit}
        offset={offset}
        handleSetOffset={setOffset}
      />
    </div>
  );
};

export default Home;
