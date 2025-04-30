import { useEffect, useState } from "react";
import { fetchPosts, PostListItem } from "../services/postService";
import PostList from "../components/posts/PostList";
import Pagination from "../components/Pagination";
import { useSearchParams } from "react-router-dom";

const PostSearch = () => {
  const [searchParasm] = useSearchParams();
  const tags = searchParasm.get("tags");

  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [offset, setOffset] = useState<number>(0);
  const [totalItems, setTotalItems] = useState<number>(0);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const limit = 10;

  useEffect(() => {
    const loadPosts = async () => {
      try {
        const data = await fetchPosts(offset, limit, null, tags);
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
  }, [offset, tags]);

  if (loading) return <p>Loading posts...</p>;
  if (error) return <p>{error}</p>;
  if (!posts) return <p>Posts not found</p>;

  const totalPages = Math.ceil(totalItems / limit);

  return (
    <>
      <h1>Post search page</h1>

      <PostList posts={posts} />

      <Pagination
        totalPages={totalPages}
        limit={limit}
        offset={offset}
        handleSetOffset={setOffset}
      />
    </>
  );
};

export default PostSearch;
