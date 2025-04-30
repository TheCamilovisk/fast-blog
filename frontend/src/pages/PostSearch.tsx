import { useEffect, useState } from "react";
import { fetchPosts, PostListItem } from "../services/postService";
import PostList from "../components/posts/PostList";
import Pagination from "../components/Pagination";
import { useSearchParams } from "react-router-dom";
import { Settings } from "../config";

const PostSearch = () => {
  const [searchParams] = useSearchParams();
  const tags = searchParams.get("tags");
  const author = searchParams.get("author");
  const offset = parseInt(searchParams.get("offset") || "0", 10);
  const limit = parseInt(searchParams.get("limit") || "10", 10);

  const handleNavigationLink = (i: number) => {
    const url = new URL("/", Settings.APP_URL);
    if (author) {
      url.searchParams.set("author", author);
    }
    if (tags) {
      url.searchParams.set("tags", tags);
    }
    url.searchParams.set("offset", i.toString());
    url.searchParams.set("limit", limit.toString());

    return url.pathname + url.search;
  };

  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [totalItems, setTotalItems] = useState<number>(0);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPosts = async () => {
      try {
        const data = await fetchPosts(offset, limit, author, tags);
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
  }, [offset, limit, tags, author]);

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
        handleNavigationLink={handleNavigationLink}
      />
    </>
  );
};

export default PostSearch;
