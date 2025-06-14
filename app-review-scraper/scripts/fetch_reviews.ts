import { getReviews } from "app-store-scraper-reviews";
import * as fs from "fs/promises";

type Game = { appId: string; name: string };

async function run() {
  const games: Game[] = JSON.parse(await fs.readFile("data/app_ids.json", "utf-8"));

  for (const game of games) {
    try {
      const reviews = await getReviews({
        appId: game.appId,
        country: "us",
        numberOfReviews: 1000
      });

      const outPath = `data/reviews_${game.appId}.json`;
      await fs.writeFile(outPath, JSON.stringify(reviews, null, 2));
      console.log(`✅ Saved ${reviews.length} reviews for ${game.name}`);
    } catch (err: any) {
      console.error(`❌ Error scraping ${game.name}:`, err.message);
    }
  }
}

run();