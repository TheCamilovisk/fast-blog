import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { AuthorProps, fetchAuthor } from "../services/authorService";
import AuthorInfo from "../components/authors/AuthorInfo";
import { fetchPosts, PostListItem } from "../services/postService";
import Pagination from "../components/Pagination";
import PostList from "../components/posts/PostList";

const Author = () => {
  const { id } = useParams();
  const [author, setAuthor] = useState<AuthorProps | null>(null);

  const [posts, setPosts] = useState<PostListItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [totalItems, setTotalItems] = useState(0);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const limit = 10;

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
  }, [id, offset]);

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
        handleNavigation={setOffset}
      />
    </article>
  );
};

export default Author;
