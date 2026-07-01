#!/usr/bin/env node

let input = "";
for await (const chunk of process.stdin) {
  input += chunk;
}

function firstToken(label) {
  const match = input.match(new RegExp(`\\[${label}_(\\d+)\\]`));
  return match ? `[${label}_${match[1]}]` : null;
}

function hasLiteral(value) {
  return input.includes(value);
}

const email = firstToken("EMAIL");
const phone = firstToken("PHONE");
const building = firstToken("BUILDING_NUMBER");
const street = firstToken("STREET_NAME");

const lines = ["Acknowledged."];

if (email) {
  lines.push(`I will email ${email}.`);
}

if (phone) {
  lines.push(`I will call ${phone}.`);
}

if (building && street) {
  let address = `${building} ${street}`;
  if (hasLiteral("Apartment 4B")) {
    address += ", Apartment 4B";
  }
  if (hasLiteral("Austin")) {
    address += ", Austin";
  }
  if (hasLiteral("Texas")) {
    address += ", Texas";
  }
  if (hasLiteral("78701")) {
    address += " 78701";
  }
  lines.push(`I will ship the packet to ${address}.`);
}

process.stdout.write(`${lines.join("\n")}\n`);
