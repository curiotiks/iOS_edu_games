import { getReviews } from 'app-store-scraper-reviews';

const reviews = await getReviews({
  country: 'us',
  appId: '479516143',
  appName: 'minecraft-dream-it-build-it',
});