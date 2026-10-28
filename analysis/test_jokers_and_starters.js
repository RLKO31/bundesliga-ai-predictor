const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf8');

console.log("=== Testing Jokers and Starter Rules in index.html ===");

// 1. Verify Joker Card in HTML
if (html.includes('id="totw-jokers-list"') && html.includes('totw-joker-card')) {
    console.log("[PASS] Joker Card container (#totw-jokers-list) exists in HTML!");
} else {
    console.error("[FAIL] Joker Card container missing!");
    process.exit(1);
}

// 2. Verify Penalty / Assist Formula in Legend
if (html.includes('differenzierter Torbewertung') && html.includes('0,70') && html.includes('0,55')) {
    console.log("[PASS] Penalty / Assist devaluation formula documented in Sabermetrics Legend!");
} else {
    console.error("[FAIL] Penalty formula documentation missing!");
    process.exit(1);
}

// 3. Verify 60+ min Starter rule in Legend
if (html.includes('Startelf-Regel') && html.includes('mindestens 60 Spielminuten')) {
    console.log("[PASS] 60+ min Starter rule documented in Legend!");
} else {
    console.error("[FAIL] 60+ min rule missing in Legend!");
    process.exit(1);
}

// 4. Verify totwData contents
const startIdx = html.indexOf('const totwData =');
const endIdx = html.indexOf(';', startIdx);
const jsonText = html.substring(startIdx + 'const totwData ='.length, endIdx).trim();
const totw = JSON.parse(jsonText);

for (let md = 1; md <= 7; md++) {
    const data = totw[String(md)];
    if (!data) {
        console.error(`[FAIL] MD ${md} missing in totwData!`);
        process.exit(1);
    }
    if (data.lineup.length !== 11) {
        console.error(`[FAIL] MD ${md} lineup length is ${data.lineup.length}, expected 11!`);
        process.exit(1);
    }
    if (!data.jokers || data.jokers.length !== 3) {
        console.error(`[FAIL] MD ${md} has ${data.jokers ? data.jokers.length : 0} jokers, expected 3!`);
        process.exit(1);
    }
    console.log(`[PASS] Matchday ${md}: 11 Starters + 3 Jokers (${data.jokers.map(j => j.name).join(', ')})`);
}

console.log("\nALL TESTS COMPLETED SUCCESSFULLY!");
