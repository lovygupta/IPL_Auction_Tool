import { test } from "@playwright/test";
import fs from "fs";

async function scrapeSeason(page: any, season: "2024" | "2025") {
  console.log(`Loading IPL stats for season ${season}`);

  await page.goto(`https://www.iplt20.com/stats/${season}`, {
    waitUntil: "domcontentloaded"
  });

  // Wait for initial table
  await page.waitForSelector("table.statsTable tbody tr");

  // Count rows before clicking View All
  const initialRowCount = await page.$$eval(
    "table.statsTable tbody tr",
    rows => rows.length
  );

  console.log(`Initial rows: ${initialRowCount}`);

  // Click "View All" if present
  const viewAll = await page.$('a:has-text("View All")');
  if (viewAll) {
    await viewAll.click();

    // Wait until more rows load
    await page.waitForFunction(
      (prevCount) => {
        const rows = document.querySelectorAll(
          "table.statsTable tbody tr"
        );
        return rows.length > prevCount;
      },
      initialRowCount
    );

    console.log("View All clicked → full table loaded");
  }

  // Scrape table
  const { headers, rows } = await page.evaluate(() => {
    const table = document.querySelector("table.statsTable");
    if (!table) throw new Error("Stats table not found");

    const headers = [
      "POS", "Player", "Team",
      "Runs", "Mat", "Inns", "NO", "HS",
      "Avg", "BF", "SR", "100", "50", "4s", "6s"
    ];

    const rows = Array.from(table.querySelectorAll("tbody tr"))
      .filter(row => row.querySelectorAll("td").length > 0)
      .map(row => {
        const tds = row.querySelectorAll("td");

        const pos = tds[0]?.innerText.trim();

        const playerTd = tds[1];
        const player =
          playerTd?.querySelector(".st-ply-name")?.innerText.trim() || "";
        const team =
          playerTd?.querySelector(".st-ply-tm-name")?.innerText.trim() || "";

        const rest = Array.from(tds)
          .slice(2)
          .map(td =>
            td.innerText.replace(/\s+/g, " ").trim()
          );

        return [pos, player, team, ...rest];
      });

    return { headers, rows };
  });

  // Convert to CSV
  const csv = [
    headers.join(","),
    ...rows.map(r => r.map(v => `"${v}"`).join(","))
  ].join("\n");

  fs.writeFileSync(`ipl_${season}_batting_stats.csv`, csv);
  console.log(
    `Saved → ipl_${season}_batting_stats.csv (${rows.length} rows)`
  );
}

test("IPL Batting Stats Scraper (Season-wise)", async ({ page }) => {
  await scrapeSeason(page, "2025");
  await scrapeSeason(page, "2024");
});