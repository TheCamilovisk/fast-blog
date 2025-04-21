import { useParams } from "react-router-dom";

const Post = () => {
  const { id } = useParams();
  return <p>Post page for post ID: {id}</p>;
};

export default Post;
