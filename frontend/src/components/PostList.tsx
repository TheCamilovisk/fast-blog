import { Link } from "react-router-dom";
import { PostListItem } from "../services/postService";

const PostList = ({ posts }: { posts: PostListItem[] }) => {
  return (
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
            <Link to={"/author/" + post.author.id}>{post.author.username}</Link>{" "}
            on {new Date(post.createdAt).toLocaleDateString()}
          </small>
        </li>
      ))}
    </ul>
  );
};

export default PostList;
