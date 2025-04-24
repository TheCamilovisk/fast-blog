import { publicApi } from "../api/axios";

export type PostListItem = {
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
};

type PostList = {
  posts: PostListItem[];
  totalItems: number;
};

export const fetchPosts = async (
  offset: number,
  limit: number
): Promise<PostList> => {
  const res = await publicApi.get("/posts", {
    params: { offset, limit },
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
};
