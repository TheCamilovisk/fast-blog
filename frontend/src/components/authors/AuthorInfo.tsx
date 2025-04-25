import { AuthorProps } from "../../services/authorService";

const AuthorInfo = ({ author }: { author: AuthorProps }) => {
  const { username, firstname, lastname, website, email, bio } = author;

  return (
    <>
      <h1>
        {firstname} {lastname} (a.k.a. {username})
      </h1>
      <p>
        Website:{" "}
        <a
          href={website?.startsWith("http") ? website : `http://${website}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          {website}
        </a>
      </p>
      <small>
        Email: <a href={`mailto:${email}`}>{email}</a>
      </small>
      {bio && <p>{bio}</p>}
    </>
  );
};

export default AuthorInfo;
