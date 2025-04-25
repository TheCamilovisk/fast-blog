import { publicApi } from "../api/axios";

export interface AuthorProps {
  id: number;
  username: string;
  firstname: string;
  lastname: string;
  email: string;
  bio: string;
  website: string | null;
}

export const fetchAuthor = async (authorId: number): Promise<AuthorProps> => {
  const res = await publicApi.get<AuthorProps>(`/authors/${authorId}`);
  return res.data;
};
