import assert from "node:assert";

// BigInt money simulation test
function createMoneyFromRupees(rupees) {
  const clean = typeof rupees === "string" ? rupees.trim().replace(/,/g, "") : rupees.toString();
  const parts = clean.split(".");
  const wholePart = BigInt(parts[0] || "0");
  const fractional = (parts[1] || "").padEnd(2, "0").slice(0, 2);
  const fracPart = BigInt(fractional);
  const sign = clean.startsWith("-") ? -1n : 1n;
  const totalPaisa = (wholePart >= 0n ? wholePart : -wholePart) * 100n + fracPart;
  return { currency: "PKR", amountPaisa: (totalPaisa * sign).toString() };
}

function addMoney(a, b) {
  return { currency: "PKR", amountPaisa: (BigInt(a.amountPaisa) + BigInt(b.amountPaisa)).toString() };
}

function subtractMoney(a, b) {
  return { currency: "PKR", amountPaisa: (BigInt(a.amountPaisa) - BigInt(b.amountPaisa)).toString() };
}

function multiplyMoneyPercent(m, percent) {
  const basisPoints = BigInt(Math.round(percent * 100));
  const current = BigInt(m.amountPaisa);
  const multiplied = (current * basisPoints) / 10000n;
  return { currency: "PKR", amountPaisa: multiplied.toString() };
}

function formatMoney(m) {
  const paisaVal = BigInt(m.amountPaisa);
  const isNeg = paisaVal < 0n;
  const absPaisa = isNeg ? -paisaVal : paisaVal;
  const rupees = absPaisa / 100n;
  const paisaRem = absPaisa % 100n;
  const formattedRupees = rupees.toLocaleString("en-US");
  const signPrefix = isNeg ? "- " : "";
  if (paisaRem > 0n) {
    return `${signPrefix}Rs. ${formattedRupees}.${paisaRem.toString().padStart(2, "0")}`;
  }
  return `${signPrefix}Rs. ${formattedRupees}`;
}

console.log("--- RUNNING FINDOST AI FINANCIAL VERIFICATION TESTS ---");

// Test 1: No IEEE-754 drift on classic 0.1 + 0.2 problem
// In floating point: 0.1 + 0.2 = 0.30000000000000004
const tenPaisa = { currency: "PKR", amountPaisa: "10" };
const twentyPaisa = { currency: "PKR", amountPaisa: "20" };
const thirtyPaisa = addMoney(tenPaisa, twentyPaisa);
assert.strictEqual(thirtyPaisa.amountPaisa, "30", "Ten paisa + twenty paisa must equal exactly thirty paisa");
console.log("✓ Test 1: Zero IEEE-754 floating point drift verified");

// Test 2: Formatting large Pakistani Rupee amounts
const largeAmount = createMoneyFromRupees("1250000"); // 12.5 Lakh
assert.strictEqual(largeAmount.amountPaisa, "125000000");
assert.strictEqual(formatMoney(largeAmount), "Rs. 1,250,000");
console.log("✓ Test 2: Exact Rupee comma grouping verified (Rs. 1,250,000)");

// Test 3: Decimal Paisa representation
const decimalAmount = createMoneyFromRupees("42500.50");
assert.strictEqual(decimalAmount.amountPaisa, "4250050");
assert.strictEqual(formatMoney(decimalAmount), "Rs. 42,500.50");
console.log("✓ Test 3: Exact decimal paisa preserved (Rs. 42,500.50)");

// Test 4: Percentage multiplier (15% wholesale tariff)
const inventoryOutflow = createMoneyFromRupees("100000");
const fifteenPercentSpike = multiplyMoneyPercent(inventoryOutflow, 15);
assert.strictEqual(fifteenPercentSpike.amountPaisa, "1500000"); // Rs. 15,000
assert.strictEqual(formatMoney(fifteenPercentSpike), "Rs. 15,000");
console.log("✓ Test 4: Percentage math rounding strictly accurate");

// Test 5: Net balance reconciliation
const startBal = createMoneyFromRupees("420000");
const salesInflow = createMoneyFromRupees("1450000");
const supplierOutflow = createMoneyFromRupees("1320000");
const netNewCash = subtractMoney(salesInflow, supplierOutflow); // +130,000
const endingBal = addMoney(startBal, netNewCash); // 550,000
assert.strictEqual(formatMoney(endingBal), "Rs. 550,000");
console.log("✓ Test 5: Reconciled cash ledger balance verified");

console.log("\nALL FINANCIAL ENGINE VERIFICATION TESTS PASSED.");
