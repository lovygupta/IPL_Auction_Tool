import { test } from "@playwright/test";
import fs from "fs";

async function scrapeBowlingSeason(page: any, season: "2024" | "2025") {
  console.log(`\n=== Bowling Stats | Season ${season} ===`);

  await page.goto(`https://www.iplt20.com/stats/${season}`, {
    waitUntil: "domcontentloaded",
  });

  /* 1️⃣ Wait for table*/
  await page.waitForSelector("table.statsTable tbody tr");

  /* 2️⃣ Open stats-type dropdown*/
  await page.click(
    "//div[contains(@class,'statsTypeFilter')]//div[contains(@class,'cSBDisplay')]"
  );

  /* 3️⃣ CLICK BOWLERS (XPath – FINAL FIX)*/
  const bowlersXPath =
    "//div[contains(@class,'cSBList') and contains(@class,'active')]//span[normalize-space()='BOWLERS']";

  await page.waitForSelector(bowlersXPath, { state: "visible" });
  await page.click(bowlersXPath);

  console.log("BOWLERS clicked");

  /* 4️⃣ Select Purple Cap  (FIXED)*/
  
  const purpleCapXPath =
    "//div[contains(@class,'cSBList') and contains(@class,'active')]" +
    "//div[contains(@class,'cSBListItems') and normalize-space()='Purple Cap']";

  await page.waitForSelector(purpleCapXPath, { state: "visible" });
  await page.click(purpleCapXPath);

  console.log("Purple Cap selected");

  // Wait for table refresh
  await page.waitForFunction(() =>
    Array.from(document.querySelectorAll("th"))
      .some(th => th.textContent?.includes("Econ"))
  );

  /* -------------------------
   5️⃣ Click View All (ANGULAR FINAL FIX)
-------------------------- */

const viewAllBtn = page.locator(
  "#bowlingTAB div.np-mostrunsTab__btn.view-all",
  { hasText: "View All" }
);

if (await viewAllBtn.isVisible()) {
  console.log("Bowling View All visible, clicking...");

  await viewAllBtn.click({ force: true });

  // Wait until Angular hides the button (ng-hide added)
  await page.waitForFunction(() => {
    const el = document.querySelector(
      "#bowlingTAB div.np-mostrunsTab__btn.view-all"
    );
    return el?.classList.contains("ng-hide");
  }, { timeout: 10000 });

  console.log("View All clicked → Bowling table expanded");
}

  /* -------------------------
     6️⃣ Scrape table
  --------------------------*/
  const { headers, rows } = await page.evaluate(() => {
    const table = document.querySelector("table.statsTable");
    if (!table) throw new Error("Stats table not found");

    const headers = [
      "POS", "Player", "Team",
      "Wkts", "Mat", "Inns", "Ov",
      "Runs", "BBI", "Avg", "Econ", "SR", "4w", "5w"
    ];

    const rows = Array.from(table.querySelectorAll("tbody tr"))
      .filter(r => r.querySelectorAll("td").length > 0)
      .map(row => {
        const tds = row.querySelectorAll("td");

        const pos = tds[0]?.innerText.trim() || "";

        const playerTd = tds[1];
        const player =
          playerTd?.querySelector(".st-ply-name")?.innerText.trim() || "";
        const team =
          playerTd?.querySelector(".st-ply-tm-name")?.innerText.trim() || "";

        const stats = Array.from(tds)
          .slice(2)
          .map(td => td.innerText.replace(/\s+/g, " ").trim());

        if (stats[5]) stats[5] = `'${stats[5]}`;

        return [pos, player, team, ...stats];
      });

    return { headers, rows };
  });

  /* 7️⃣ CSV Export*/
  const csv = [
    headers.join(","),
    ...rows.map(r => r.map(v => `"${v}"`).join(","))
  ].join("\n");

  fs.writeFileSync(
    `ipl_${season}_bowling_stats.csv`,
    csv
  );

  console.log(
    `Saved → ipl_${season}_bowling_stats.csv (${rows.length} rows)`
  );
}

test("IPL Bowling Stats Scraper (Season-wise)", async ({ page }) => {
  await scrapeBowlingSeason(page, "2025");
  await scrapeBowlingSeason(page, "2024");
});