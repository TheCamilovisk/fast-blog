const Pagination = ({
  totalPages,
  limit,
  offset,
  handleNavigation: handleNavigation,
}: {
  totalPages: number;
  limit: number;
  offset: number;
  handleNavigation: (newOffset: number) => void;
}) => {
  return (
    <div>
      {Array.from({ length: totalPages }, (_, i) => (
        <button
          key={i}
          onClick={() => handleNavigation(i * limit)}
          disabled={offset === i * limit}
          style={{ margin: "0 0.25 rem" }}
        >
          {(i + 1) * limit}
        </button>
      ))}
    </div>
  );
};

export default Pagination;
