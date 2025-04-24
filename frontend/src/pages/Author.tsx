import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

type AuthorProps = {
  id: string;
  username: string;
  firstname: string;
  lastname: string;
};

const Author = () => {
  const { id } = useParams();
  const [author, setAuthor] = useState<AuthorProps | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAuthor = async () => {
      try {
        const response = await fetch(`http://localhost:8000/authors/${id}`);
        if (!response.ok) {
          throw new Error("Failed to fetch author");
        }
        const data: AuthorProps = await response.json();
        setAuthor(data);
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (id) fetchAuthor();
  }, [id]);

  if (loading) return <p>Loading author...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!author) return <p>Author not found</p>;

  return (
    <article>
      <h1>
        {author.firstname} {author.lastname} (a.k.a. {author.username})
      </h1>
    </article>
  );
};

export default Author;
