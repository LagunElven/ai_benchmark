const { validateRegistration } = require('../registration-form');

const input = {
  email: '  Ada@example.test ',
  password: 'SecurePassword7',
  confirmPassword: 'SecurePassword7',
  accountType: ' BUSINESS ',
  companyName: '  Example SA ',
  vatNumber: ' fr 12345678 ',
  termsAccepted: true,
};
const result = validateRegistration(input);
if (!result.valid || Object.keys(result.errors).length !== 0) {
  throw new Error('valid registration was rejected');
}
if (result.value.email !== 'ada@example.test' || result.value.accountType !== 'business'
    || result.value.companyName !== 'Example SA' || result.value.vatNumber !== 'FR12345678') {
  throw new Error('registration values were not normalized');
}
if (input.email !== '  Ada@example.test ' || input.vatNumber !== ' fr 12345678 ') {
  throw new Error('input was mutated');
}
console.log('public registration checks passed');
