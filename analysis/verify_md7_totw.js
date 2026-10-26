const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf8');

const startIdx = html.indexOf('const totwData =');
const endIdx = html.indexOf(';', startIdx);
const jsonText = html.substring(startIdx + 'const totwData ='.length, endIdx).trim();

const totw = JSON.parse(jsonText);
console.log("Matchdays in totwData:", Object.keys(totw));

const md7 = totw["7"];
if (!md7) {
    console.error("FAIL: Matchday 7 not found in totwData!");
    process.exit(1);
}

console.log("MD7 Title:", md7.title);
console.log("MD7 Formation:", md7.formation);
console.log("MD7 MVP:", md7.mvp);
console.log("MD7 Coach:", md7.coach);
console.log("MD7 Fixtures count:", md7.fixtures_summary.length);
console.log("MD7 Lineup count:", md7.lineup.length);

if (md7.lineup.length !== 11) {
    console.error("FAIL: Expected 11 players, found:", md7.lineup.length);
    process.exit(1);
}

md7.lineup.forEach((p, idx) => {
    console.log(`  ${idx+1}. [${p.pos}] ${p.name} (${p.club}) - x:${p.x}% y:${p.y}% | ${p.stat} | ${p.highlight}`);
});

console.log("\nALL VERIFICATIONS PASSED!");
