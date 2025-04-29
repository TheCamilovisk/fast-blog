import axios from "axios";
import { publicApi } from "../api/axios";
import PostList from "../components/posts/PostList";

export interface PostListItem {
  id: number;
  title: string;
  subtitle: string;
  createdAt: string;
  author: {
    id: number;
    username: string;
    firstname: string;
    lastname: string;
  };
}

interface PostList {
  posts: PostListItem[];
  totalItems: number;
}

export interface PostProps {
  title: string;
  subtitle: string;
  content: string;
  updated_at: string;
  published_at: string;
  author: {
    id: number;
    username: string;
  };
  tags: string[];
}

export const fetchPosts = async (
  offset: number,
  limit: number,
  author: string | null = null,
  tags: string | null = null
): Promise<PostList> => {
  try {
    const res = await publicApi.get("/posts", {
      params: { offset, limit, author_username: author, tags: tags },
    });

    const mappedPosts = res.data.posts.map(
      (post: {
        id: number;
        title: string;
        subtitle: string;
        created_at: string;
        author: {
          id: number;
          username: string;
          firstname: string;
          lastname: string;
        };
      }): PostListItem => ({
        id: post.id,
        title: post.title,
        subtitle: post.subtitle,
        createdAt: post.created_at,
        author: post.author,
      })
    );

    return {
      posts: mappedPosts,
      totalItems: res.data.total_items,
    };
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail);
    } else {
      throw error;
    }
  }
};

export const fetchPostDetail = async (postId: number): Promise<PostProps> => {
  try {
    const res = await publicApi.get<PostProps>(`/posts/${postId}`);
    return res.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data.detail);
    } else {
      throw error;
    }
  }
};
