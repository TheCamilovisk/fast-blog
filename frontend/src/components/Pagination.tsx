const Pagination = ({
  totalPages,
  limit,
  offset,
  handleSetOffset,
}: {
  totalPages: number;
  limit: number;
  offset: number;
  handleSetOffset: (newOffset: number) => void;
}) => {
  return (
    <div>
      {Array.from({ length: totalPages }, (_, i) => (
        <button
          key={i}
          onClick={() => handleSetOffset(i * limit)}
          disabled={offset === i * limit}
          style={{ margin: "0 0.25 rem" }}
        >
          {i + 1}
        </button>
      ))}
    </div>
  );
};

export default Pagination;
