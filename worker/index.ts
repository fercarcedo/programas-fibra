import { WorkerEntrypoint } from "cloudflare:workers";

interface Env {
  BUCKET_GEO: R2Bucket;
}

export default class extends WorkerEntrypoint<Env> {
  async fetch(request: Request) {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/data/")) {
      const key = url.pathname.replace(/^\/data\//, "");

      if (key.startsWith("aggregated-")) {
        const object = await this.env.BUCKET_GEO.get(key);

        if (!object) {
          return new Response("Not found", { status: 404 });
        }
        
        return new Response(object.body, {
          headers: {
            "content-type": "application/json; charset=UTF-8",
            "cache-control": "public, max-age=31536000, immutable",
          },
        });
      }
    }

    if (url.pathname.startsWith("/api/")) {
      return Response.json({
        name: "Cloudflare",
      });
    }
    return new Response(null, { status: 404 });
  }
}
