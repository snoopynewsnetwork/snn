declare namespace Cloudflare {
  interface GlobalProps {
    mainModule: typeof import("../src/index");
  }
  interface Env {
    NEWSROOM: DurableObjectNamespace<import("../src/index").Newsroom>;
    ASSETS: Fetcher;
    ADMIN_TOKEN: string;
  }
}
