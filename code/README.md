# IPL Stats Scraper 🏏

A Playwright-based scraper to extract IPL batting and bowling statistics
directly from the official IPL website.

## Features
- Batting & Bowling stats
- Season-wise scraping (2024, 2025)
- Handles Angular-based UI
- CSV export
- Playwright automation

## Tech Stack
- Playwright
- TypeScript
- Node.js

## Make sure to change headless state in playwright.config.js
## How to Run

```bash
npm install
npx playwright install
npx playwright tests
headless: true,