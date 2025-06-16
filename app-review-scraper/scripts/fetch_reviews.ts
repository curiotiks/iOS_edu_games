// @ts-ignore
import store from 'app-store-scraper';
import * as fs from 'fs/promises';

type Input = {
  appId: string;
  country?: string;
};

async function fetchAllReviews({ appId, country = 'us' }: Input) {
  let page = 1;
  const allReviews: any[] = [];

  while (true) {
    try {
      const reviews = await store.reviews({
        id: appId,
        country,
        page,
        sort: store.sort.NEWEST
      });

      if (!reviews || reviews.length === 0) {
        console.log(`✅ No more reviews on page ${page}.`);
        break;
      }

      console.log(`📄 Fetched ${reviews.length} reviews on page ${page}`);
      allReviews.push(...reviews);
      page++;

      // Delay to avoid being throttled
      await new Promise(res => setTimeout(res, 1000));
    } catch (err: any) {
      console.error(`❌ Error on page ${page}:`, err.message || err);
      break;
    }
  }

  const outPath = `data/reviews_${appId}.json`;
  await fs.writeFile(outPath, JSON.stringify(allReviews, null, 2));
  console.log(`💾 Saved ${allReviews.length} reviews to ${outPath}`);
}

// If run directly (i.e., not imported), get args from command line
const [, , appId, countryArg] = process.argv;

if (!appId) {
  console.error('❌ Please provide an app ID.');
  process.exit(1);
}

fetchAllReviews({ appId, country: countryArg || 'us' });