import { getReviews } from "app-store-scraper-reviews";
import * as fs from "fs";

type Game = { appId: string; name: string };

async function run() {
  const games: Game[] = JSON.parse(await fs.promises.readFile("data/app_ids.json", "utf-8"));

  for (const game of games) {
    try {
      const reviews = await getReviews({
        appId: game.appId,
        country: "us",
        numberOfReviews: 1000
      });

      if (!Array.isArray(reviews)) throw new Error("Invalid response");

      const outPath = `data/reviews_${game.appId}.json`;
      await fs.promises.writeFile(outPath, JSON.stringify(reviews, null, 2));
      console.log(`✅ Saved ${reviews.length} reviews for ${game.name}`);
    } catch (err: any) {
       console.error(`❌ Error scraping ${game.name}:`, err);
    }
  }
}

run();