import { Link } from "react-router-dom";
import { PostProps } from "../../services/postService";

const toLocaleDateString = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString("en-US", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
};

const PostDetail = ({ post }: { post: PostProps }) => {
  const {
    title,
    subtitle,
    published_at,
    updated_at,
    tags,
    author: { id: author_id, username },
  } = post;
  return (
    <>
      <h1>{title}</h1>
      <h2>{subtitle}</h2>
      <small>
        by <Link to={"/author/" + author_id}>{username}</Link> on{" "}
        {toLocaleDateString(published_at)}
      </small>
      <br />
      <small>last updated on {toLocaleDateString(updated_at)}</small>
      <br />
      <small>
        Tags:{" "}
        {tags.map((tag) => (
          <span>{tag}</span>
        ))}
      </small>
    </>
  );
};

export default PostDetail;
