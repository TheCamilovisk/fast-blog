import { useParams } from "react-router-dom";

const Author = () => {
  const { id } = useParams();
  return <p>Author page for author with ID: {id}</p>;
};

export default Author;
