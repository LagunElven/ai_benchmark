function validateRegistration(input) {
  const source = input && typeof input === 'object' ? input : {};
  const text = (field) => typeof source[field] === 'string' ? source[field].trim() : '';
  const email = text('email').toLowerCase();
  const password = typeof source.password === 'string' ? source.password : '';
  const confirmPassword = typeof source.confirmPassword === 'string'
    ? source.confirmPassword : '';
  const accountType = text('accountType').toLowerCase();
  const companyName = text('companyName');
  const vatNumber = text('vatNumber').replace(/\s+/g, '').toUpperCase();
  const errors = {};
  const add = (field, code) => {
    if (!errors[field]) errors[field] = [];
    errors[field].push(code);
  };

  if (!email) add('email', 'required');
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) add('email', 'format');
  if (!password) add('password', 'required');
  else {
    if (password.length < 12) add('password', 'minLength');
    if (!/[A-Z]/.test(password)) add('password', 'uppercase');
    if (!/[a-z]/.test(password)) add('password', 'lowercase');
    if (!/[0-9]/.test(password)) add('password', 'digit');
    if (/\s/.test(password)) add('password', 'whitespace');
  }
  if (!confirmPassword) add('confirmPassword', 'required');
  else if (confirmPassword !== password) add('confirmPassword', 'mismatch');
  if (!accountType) add('accountType', 'required');
  else if (!['individual', 'business'].includes(accountType)) add('accountType', 'unsupported');
  if (accountType === 'business') {
    if (!companyName) add('companyName', 'required');
    if (!vatNumber) add('vatNumber', 'required');
    else if (!/^[A-Z]{2}[A-Z0-9]{8,14}$/.test(vatNumber)) add('vatNumber', 'format');
  }
  if (source.termsAccepted !== true) add('termsAccepted', 'accepted');

  const value = {
    email,
    password,
    confirmPassword,
    accountType,
    companyName,
    vatNumber,
    termsAccepted: source.termsAccepted,
  };
  return { valid: Object.keys(errors).length === 0, value, errors };
}

module.exports = { validateRegistration };
