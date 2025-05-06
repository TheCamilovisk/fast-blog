const Pagination = ({
  totalPages,
  limit,
  offset,
  handlePageChange: handlePageChange,
}: {
  totalPages: number;
  limit: number;
  offset: number;
  handlePageChange: (page: number) => void;
}) => {
  return (
    <div>
      {Array.from({ length: totalPages }, (_, i) =>
        offset !== i * limit ? (
          <button key={i} onClick={() => handlePageChange(i)}>
            {i + 1}
          </button>
        ) : (
          i + 1
        )
      )}
    </div>
  );
};

export default Pagination;
