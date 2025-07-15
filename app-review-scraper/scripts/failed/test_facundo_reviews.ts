// @ts-ignore
import store from 'app-store-scraper';

async function run() {
  try {
    const reviews = await store.reviews({
      id: 553834731,     // Candy Crush Saga
      country: 'us',
      page: 1,           // first page of reviews
      sort: store.sort.NEWEST
    });
    console.log(reviews);
    console.log(`Fetched ${reviews.length} reviews.`);
  } catch (err) {
    console.error('Error fetching reviews:', err);
  }
}

run();