export default {
  api: {
    baseUrl: process.env.REACT_APP_BACKEND_URL || "http://localhost:8000",
    endpoints: {
      scrape: "/scrape-emails",
      subscribe: "/create-checkout-session"
    }
  },
  stripe: {
    publishableKey: process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY
  }
};