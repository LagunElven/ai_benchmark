const { validateRegistration } = require('./registration-form');

function has(result, field, code) {
  return Array.isArray(result.errors[field]) && result.errors[field].includes(code);
}

const base = {
  email: 'person@example.test',
  password: 'ValidPassword7',
  confirmPassword: 'ValidPassword7',
  accountType: 'individual',
  termsAccepted: true,
};
const individual = validateRegistration({ ...base, companyName: ' ', vatNumber: ' ' });
if (!individual.valid || Object.keys(individual.errors).length !== 0) {
  throw new Error('valid individual form was rejected');
}

const invalid = validateRegistration({
  ...base,
  email: 'bad address',
  password: 'short',
  confirmPassword: 'different',
  accountType: 'business',
  companyName: ' ',
  vatNumber: 'FR 12',
  termsAccepted: false,
  extra: 'must not escape',
});
if (invalid.valid || !has(invalid, 'email', 'format') || !has(invalid, 'password', 'minLength')
    || !has(invalid, 'password', 'uppercase') || !has(invalid, 'password', 'digit')
    || !has(invalid, 'confirmPassword', 'mismatch') || !has(invalid, 'companyName', 'required')
    || !has(invalid, 'vatNumber', 'format') || !has(invalid, 'termsAccepted', 'accepted')) {
  throw new Error('invalid field or cross-field errors were missed');
}
if (Object.prototype.hasOwnProperty.call(invalid.value, 'extra')) {
  throw new Error('unknown input field escaped into normalized value');
}

const unsupported = validateRegistration({ ...base, accountType: 'partner' });
if (unsupported.valid || !has(unsupported, 'accountType', 'unsupported')) {
  throw new Error('unsupported account type was accepted');
}
console.log('hidden registration checks passed');
