import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { PostProps, fetchPostDetail } from "../services/postService";
import PostDetail from "../components/posts/PostDetail";
import PostContent from "../components/posts/PostContent";

const Post = () => {
  const { id } = useParams();

  const [post, setPost] = useState<PostProps | null>(null);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const postData = await fetchPostDetail(Number(id));
        setPost(postData);
      } catch (error) {
        setError("Error fetching post data: " + error);
      } finally {
        setLoading(false);
      }
    };

    if (id) fetchData();
  }, [id]);

  if (loading) return <p>Loading post...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!post) return <p>Post not found</p>;

  return (
    <article>
      <PostDetail post={post} />
      <PostContent content={post?.content} />
    </article>
  );
};

export default Post;
