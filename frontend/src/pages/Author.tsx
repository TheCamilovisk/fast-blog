import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { AuthorProps, fetchAuthor } from "../services/authorService";
import AuthorInfo from "../components/authors/AuthorInfo";
import { fetchPosts, PostListItem } from "../services/postService";
import Pagination from "../components/Pagination";
import PostList from "../components/posts/PostList";
import { Settings } from "../config";

const Author = () => {
  const { id } = useParams();
  const [author, setAuthor] = useState<AuthorProps | null>(null);

  const [searchParams] = useSearchParams();
  const offset = parseInt(searchParams.get("offset") || "0", 10);
  const limit = parseInt(searchParams.get("limit") || "10", 10);

  const handleNavigationLink = (i: number) => {
    const url = new URL(`/author/${id}`, Settings.APP_URL);
    url.searchParams.set("offset", i.toString());
    url.searchParams.set("limit", limit.toString());

    return url.pathname + url.search;
  };

  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [totalItems, setTotalItems] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const authorData = await fetchAuthor(Number(id));
        setAuthor(authorData);

        const postsData = await fetchPosts(offset, limit, authorData.username);
        setPosts(postsData.posts);
        setTotalItems(postsData.totalItems);
      } catch (error) {
        if (error instanceof Error) {
          setError(error.message);
        }
      } finally {
        setLoading(false);
      }
    };

    if (id) fetchData();
  }, [id, limit, offset]);

  const totalPages = Math.ceil(totalItems / limit);

  if (loading) return <p>Loading author...</p>;
  if (error) return <p>{error}</p>;
  if (!author) return <p>Author not found</p>;

  return (
    <article>
      <AuthorInfo author={author} />

      <h1>{author.username}'s Posts</h1>

      <PostList posts={posts} />

      <Pagination
        totalPages={totalPages}
        limit={limit}
        offset={offset}
        handleNavigationLink={handleNavigationLink}
      />
    </article>
  );
};

export default Author;
