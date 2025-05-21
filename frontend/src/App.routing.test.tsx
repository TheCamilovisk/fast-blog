import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("App routing", () => {
  it('shows Home page at "/"', () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByText("Home Page")).toBeInTheDocument();
  });

  it('shows Posts page at "/posts"', () => {
    render(
      <MemoryRouter initialEntries={["/posts"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByText("Posts Page")).toBeInTheDocument();
  });

  it("shows Not Found page at unknown route", () => {
    render(
      <MemoryRouter initialEntries={["/something-that-does-not-exist"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByText("Page Not Found")).toBeInTheDocument();
  });
});
