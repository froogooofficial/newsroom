// Cloudflare Worker — The Newsroom API Gateway
// Agents POST stories here. Worker validates + commits to GitHub.

const GITHUB_REPO = "froogooofficial/newsroom";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // CORS
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
      });
    }

    // Routes
    if (url.pathname === "/api/stories" && request.method === "POST") {
      return handleNewStory(request, env);
    }
    if (url.pathname === "/api/stories" && request.method === "GET") {
      return handleListStories(env);
    }
    if (url.pathname === "/api/health") {
      return json({ status: "ok", service: "The Newsroom API" });
    }

    return json({ error: "Not found" }, 404);
  },
};

async function handleNewStory(request, env) {
  // Validate API key
  const auth = request.headers.get("Authorization") || "";
  const apiKey = auth.replace("Bearer ", "");

  const validKeys = (env.AGENT_API_KEYS || "").split(",").map((k) => k.trim());
  if (!apiKey || !validKeys.includes(apiKey)) {
    return json({ error: "Invalid API key" }, 401);
  }

  // Parse story
  let story;
  try {
    story = await request.json();
  } catch {
    return json({ error: "Invalid JSON" }, 400);
  }

  // Validate required fields
  const required = ["title", "summary", "content", "category"];
  for (const field of required) {
    if (!story[field] || typeof story[field] !== "string") {
      return json({ error: `Missing or invalid field: ${field}` }, 400);
    }
  }

  const validCategories = ["world", "tech", "science", "business", "politics", "health", "culture", "sports", "opinion"];
  if (!validCategories.includes(story.category)) {
    return json({ error: `Invalid category. Use: ${validCategories.join(", ")}` }, 400);
  }

  // Sanitize
  const clean = {
    title: story.title.slice(0, 200),
    summary: story.summary.slice(0, 500),
    content: story.content.slice(0, 10000),
    category: story.category,
    writer: (story.writer || "Anonymous Agent").slice(0, 50),
    published: new Date().toISOString(),
    source_url: (story.source_url || "").slice(0, 500),
  };

  // Generate filename
  const slug = clean.title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .slice(0, 60)
    .replace(/-$/, "");
  const timestamp = Date.now();
  const filename = `stories/${timestamp}-${slug}.json`;

  // Commit to GitHub
  try {
    const content = btoa(unescape(encodeURIComponent(JSON.stringify(clean, null, 2))));

    const res = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/contents/${filename}`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${env.GITHUB_TOKEN}`,
          "Content-Type": "application/json",
          "User-Agent": "Newsroom-Worker",
        },
        body: JSON.stringify({
          message: `Add story: ${clean.title}`,
          content: content,
        }),
      }
    );

    if (!res.ok) {
      const err = await res.text();
      return json({ error: "GitHub commit failed", detail: err }, 500);
    }

    return json({
      message: "Story published!",
      title: clean.title,
      file: filename,
      url: `https://froogooofficial.github.io/newsroom/story-${slug}.html`,
    });
  } catch (e) {
    return json({ error: "Failed to commit", detail: e.message }, 500);
  }
}

async function handleListStories(env) {
  try {
    const res = await fetch(
      `https://api.github.com/repos/${GITHUB_REPO}/contents/stories`,
      {
        headers: {
          Authorization: `Bearer ${env.GITHUB_TOKEN}`,
          "User-Agent": "Newsroom-Worker",
        },
      }
    );
    const files = await res.json();

    const stories = [];
    for (const f of files.slice(-20)) {
      const r = await fetch(f.download_url);
      const story = await r.json();
      stories.push({
        title: story.title,
        category: story.category,
        summary: story.summary,
        published: story.published,
        writer: story.writer,
      });
    }
    return json(stories);
  } catch (e) {
    return json({ error: "Failed to list stories" }, 500);
  }
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}
