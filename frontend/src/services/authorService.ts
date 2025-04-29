import axios from "axios";
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
  try {
    const res = await publicApi.get<AuthorProps>(`/authors/${authorId}`);
    return res.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail);
    } else {
      throw error;
    }
  }
};
