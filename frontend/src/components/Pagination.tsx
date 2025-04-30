import { Link } from "react-router-dom";

const Pagination = ({
  totalPages,
  limit,
  offset,
  handleNavigationLink: handleNavigationLink,
}: {
  totalPages: number;
  limit: number;
  offset: number;
  handleNavigationLink: (newOffset: number) => string;
}) => {
  return (
    <div>
      {Array.from({ length: totalPages }, (_, i) =>
        offset !== i * limit ? (
          <Link to={handleNavigationLink(i * limit)}>{(i + 1) * limit}</Link>
        ) : (
          (i + 1) * limit
        )
      )}
    </div>
  );
};

export default Pagination;
